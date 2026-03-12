import frappe
from frappe.model.document import Document
from frappe import _
import json
from frappe.utils import getdate, add_days

class AttendanceCollection(Document):
    pass

@frappe.whitelist()
def process_overtime_request(docname, selected_rows):
    return create_dispatched_request(docname, selected_rows, "Overtime Request")

@frappe.whitelist()
def process_compensatory_leave_request(docname, selected_rows):
    return create_dispatched_request(docname, selected_rows, "Compensatory Leave Request")

def create_dispatched_request(docname, selected_rows, target_doctype):
    if isinstance(selected_rows, str):
        selected_rows = json.loads(selected_rows)
    working_hours = frappe.db.get_single_value("HR Settings", "standard_working_hours") or 0
    if not working_hours or working_hours <= 0:
        frappe.throw(_("Please set Standard Working Hours in HR Settings before processing requests."))
    att_col_doc = frappe.get_doc("Attendance Collection", docname)
    
    # 1. Filter and Validate Rows
    target_checkins = [row for row in att_col_doc.employee_checkin_list if row.name in selected_rows and row.status != "Paid"]
    if not target_checkins:
        frappe.throw(_("No valid or unpaid rows selected."))

    # 2. Strict Validation for Compensatory Leave
    if target_doctype == "Compensatory Leave Request":
        for row in target_checkins:
            if not row.attendance:
                frappe.throw(_("Row for {0} does not have an Attendance record. Please create/sync attendance first.").format(row.attendance_date))
            
            # Check if the date is actually a holiday
            is_holiday = check_if_holiday(row.attendance, row.attendance_date)
            if not is_holiday:
                frappe.throw(_("Date {0} is not a Holiday. Compensatory Leave is only allowed for Holidays.").format(row.attendance_date))

    # 3. Initialize the Request Document
    new_request = frappe.new_doc(target_doctype)
    new_request.employee = att_col_doc.employee
    new_request.status = "Draft"
    
    # 4. Map Fields based on DocType
    if target_doctype == "Overtime Request":
        new_request.overtime_request_date = frappe.utils.nowdate()
        days = att_col_doc.days_to_be_deducted or 0
        hours = att_col_doc.hours_to_be_deducted or 0
        total_ot = (8 * days) + hours

        for checkin in target_checkins:
            new_request.append("ot_list", {
                "date": checkin.attendance_date,
                "shift_type": get_shift_for_checkin(att_col_doc.employee, checkin),
                "overtime_hours": total_ot
            })
    
    elif target_doctype == "Compensatory Leave Request":
        sorted_dates = sorted([getdate(r.attendance_date) for r in target_checkins])
        new_request.work_from_date = sorted_dates[0]
        new_request.work_end_date = sorted_dates[-1]
        new_request.reason =att_col_doc.reason or  _("Generated from Attendance Collection")
        if not new_request.leave_type:
            new_request.leave_type = frappe.db.get_value("Leave Type", {"is_compensatory": 1}, "name")

    new_request.insert(ignore_permissions=True)

    # 5. Finalize: Update Status and Logs
    for checkin in target_checkins:
        checkin.status = "Paid"
        log_doc = frappe.new_doc("Attendance Collection Log")
        log_doc.employee = att_col_doc.employee
        log_doc.attendance_date = checkin.attendance_date
        log_doc.inn = checkin.inn 
        log_doc.out = checkin.out
        log_doc.employee_checkin = checkin.employee_checkin
        log_doc.attendance = checkin.attendance
        log_doc.attendance_collection = att_col_doc.name
        log_doc.data_dispatched_to = target_doctype
        log_doc.reference_document = new_request.name
        log_doc.deducted_days = att_col_doc.total_days or 0
        log_doc.deducted_hours = att_col_doc.total_hours or 0
        log_doc.status = "Paid"
        log_doc.insert(ignore_permissions=True)

    att_col_doc.days_to_be_deducted = 0
    att_col_doc.hours_to_be_deducted = 0
    att_col_doc.utilize_it_on = None
    att_col_doc.save(ignore_permissions=True)

    return new_request.name

def check_if_holiday(attendance_id, date):
    """Checks if the attendance record is linked to a holiday"""
    att_doc = frappe.get_value("Attendance", attendance_id, ["shift", "company"], as_dict=1)
    if not att_doc: return False
    
    holiday_list = frappe.db.get_value("Shift Type", att_doc.shift, "holiday_list")
    if not holiday_list:
        holiday_list = frappe.db.get_value("Company", att_doc.company, "default_holiday_list")
        
    if holiday_list:
        return frappe.db.exists("Holiday", {"parent": holiday_list, "holiday_date": date})
    return False

def get_shift_for_checkin(employee, checkin):
    shift_type = None
    if checkin.attendance:
        shift_type = frappe.db.get_value("Attendance", checkin.attendance, "shift")
    if not shift_type:
        shift_type = frappe.db.get_value("Employee", employee, "default_shift")
    return shift_type
@frappe.whitelist()
def sync_attendance_to_collection_for_all_employees():
    """Blind fetch for every active employee"""
    employees = frappe.get_all("Employee", filters={"status": "Active"}, pluck="name")
    for emp in employees:
        sync_remaining_attendance_for_employee(emp)
    return True
    
@frappe.whitelist()
def sync_attendance_to_collection_bulk(employee_ids):
    """Blind fetch for specific employees"""
    if isinstance(employee_ids, str):
        employee_ids = json.loads(employee_ids)
    for emp in employee_ids:
        sync_remaining_attendance_for_employee(emp)
    return True

def sync_remaining_attendance_for_employee(employee):
    """Gathers all valid dates (Holiday or Off-shift) and builds the collection, skipping already logged records."""
    
    # 1. Fetch relevant Attendance records
    attendances = frappe.get_all(
        "Attendance",
        filters={"employee": employee, "docstatus": 1, "status": ["in", ["Present", "Half Day", "Work From Home"]]},
        fields=["name", "attendance_date", "shift", "company", "employee", "employee_name"]
    )
    
    holiday_dates = set()
    attendance_map = {} 
    for att in attendances:
        att_date = getdate(att.attendance_date)
        attendance_map[att_date] = att
        if is_date_holiday(att):
            holiday_dates.add(att_date)

    # 2. Fetch Off-shift Checkins
    offshift_checkins = frappe.get_all(
        "Employee Checkin",
        filters={"employee": employee, "offshift": 1},
        fields=["name", "time"]
    )
    
    offshift_dates = set()
    for c in offshift_checkins:
        offshift_dates.add(getdate(c.time))

    dates_to_process = holiday_dates.union(offshift_dates)
    if not dates_to_process:
        return 

    # 3. Fetch ALREADY PROCESSED check-ins from the Log to skip them
    # This prevents adding rows that are already 'Paid' or 'Processed'
    processed_checkins = frappe.get_all(
        "Attendance Collection Log",
        filters={"employee": employee, "status": "Paid"},
        pluck="employee_checkin"
    )

    # 4. Handle Collection Document
    collection_name = frappe.db.get_value("Attendance Collection", {"employee": employee}, "name")
    if collection_name:
        coll_doc = frappe.get_doc("Attendance Collection", collection_name)
    else:
        coll_doc = frappe.new_doc("Attendance Collection")
        coll_doc.employee = employee
        coll_doc.employee_name = frappe.db.get_value("Employee", employee, "employee_name")

    # Keep existing rows that are already 'Paid' or not in the current processing window
    existing_rows = coll_doc.get("employee_checkin_list", [])
    new_rows = []
    for row in existing_rows:
        row_date = getdate(row.attendance_date)
        # If the date is being re-processed, we remove the "New" row and rebuild it
        # But we KEEP "Paid" rows in the table for history
        if row_date not in dates_to_process or row.status == "Paid":
            new_rows.append(row)
            
    coll_doc.set("employee_checkin_list", new_rows)

    # 5. Process target dates and pairs
    for target_date in dates_to_process:
        start_time = f"{target_date} 00:00:00"
        end_time = f"{target_date} 23:59:59"
        
        day_checkins = frappe.get_all(
            "Employee Checkin",
            filters={
                "employee": employee,
                "time": ["between", [start_time, end_time]]
            },
            fields=["name", "time", "log_type", "offshift"],
            order_by="time asc"
        )

        pairs = get_in_out_pairs(day_checkins)
        att_doc = attendance_map.get(target_date) 

        for pair in pairs:
            checkin_ref = pair.get("checkin_ref")
            
            # CHECK: Skip if this specific check-in exists in the Log
            if checkin_ref in processed_checkins:
                continue

            coll_doc.append("employee_checkin_list", {
                "attendance_date": target_date,
                "inn": pair.get("inn"),
                "out": pair.get("out"),
                "employee_checkin": checkin_ref, 
                "attendance": att_doc.name if att_doc else None, 
                "status": "New"
            })

    coll_doc.save(ignore_permissions=True)

def is_date_holiday(doc):
    holiday_list = None
    if doc.shift:
        holiday_list = frappe.db.get_value("Shift Type", doc.shift, "holiday_list")
    
    if not holiday_list and doc.company:
        holiday_list = frappe.db.get_value("Company", doc.company, "default_holiday_list")

    if holiday_list:
        return frappe.db.exists("Holiday", {
            "parent": holiday_list,
            "holiday_date": doc.attendance_date
        })
    return False

def get_in_out_pairs(checkins):
    if not checkins:
        return [{"inn": None, "out": None, "checkin_ref": None}]

    pairs = []
    current_in = None

    for log in checkins:
        if log.log_type == "IN":
            if current_in:
                pairs.append({"inn": current_in.time, "out": None, "checkin_ref": current_in.name})
            current_in = log
        elif log.log_type == "OUT":
            if current_in:
                pairs.append({"inn": current_in.time, "out": log.time, "checkin_ref": current_in.name})
                current_in = None
            else:
                pairs.append({"inn": None, "out": log.time, "checkin_ref": log.name})

    if current_in:
        pairs.append({"inn": current_in.time, "out": None, "checkin_ref": current_in.name})

    return pairs