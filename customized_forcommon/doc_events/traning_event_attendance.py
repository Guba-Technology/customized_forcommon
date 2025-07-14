from frappe.utils import getdate
import frappe
from collections import defaultdict

def validate_training_event(doc, method):
    validate_attendance_dates(doc, method)
    calculate_total_present_days(doc)
    clear_attendance_table_or_employees(doc)

def validate_attendance_dates(doc, method):
    if doc.custom_attendance_table:
        attend_employee_date = set()
        for attendance in doc.custom_attendance_table:
            if attendance.attendance_date:
                attendance_date = getdate(attendance.attendance_date)
                
                # Check date bounds
                if attendance_date < getdate(doc.start_time):
                    frappe.throw(
                        f"Attendance date {attendance_date} cannot be before the start date {getdate(doc.start_time)}."
                    )
                if attendance_date > getdate(doc.end_time):
                    frappe.throw(
                        f"Attendance date {attendance_date} cannot be after the end date {getdate(doc.end_time)}."
                    )
                
                # Check for duplicate employee+date
                if attendance.employee:
                    key = (attendance.employee, attendance_date)
                    if key in attend_employee_date:
                        frappe.throw(
                            f"Employee {attendance.employee} has duplicate attendance entries on {attendance_date}."
                        )
                    attend_employee_date.add(key)

def calculate_total_present_days(doc):
    # Always clear the total present days table
    doc.set("custom_total_present_days", [])

    # If attendance table is empty, we're done
    if not doc.custom_attendance_table:
        return

    # Count present days per employee
    employee_attendance = defaultdict(set)

    for row in doc.custom_attendance_table:
        if row.employee and row.attendance_date:
            employee_attendance[row.employee].add(getdate(row.attendance_date))

    # Populate total present days
    for employee, dates in employee_attendance.items():
        doc.append("custom_total_present_days", {
            "employee": employee,
            "employee_name": frappe.db.get_value("Employee", employee, "employee_name"),
            "total_present_days": len(dates)
        })

def clear_attendance_table_or_employees(doc):
    if doc.custom_daily_attendance_required:
        # clear Employees table if daily attendance is required
        doc.set("employees", [])
    else:
        # clear Custom Attendance Table if daily attendance is not required
        doc.set("custom_attendance_table", [])
        doc.set("custom_total_present_days", [])