# Copyright (c) 2026, Guba Technology and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.model.document import Document
import json

class BulkEmployeCheckin(Document):
	pass


@frappe.whitelist()
def get_eligible_employees(from_date, to_date, checkin_type, shift=None):

    filters = {"status": "Active"}
    if shift:
        filters["default_shift"] = shift

    employees = frappe.get_all("Employee", filters=filters, fields=["name", "default_shift"])
    
    if not employees:
        return []

    existing_checkins = frappe.db.get_all(
        "Employee Checkin",
        filters={
            "time": ["between", [from_date, to_date]],
			"log_type": checkin_type
        },
        fields=["employee"],
        pluck="employee"
    )
    print("Existing Checkins: ", existing_checkins)
    
    eligible_employees = [emp for emp in employees if emp.name not in existing_checkins]
    
    return eligible_employees


@frappe.whitelist()
def create_bulk_checkins(employees, log_type, time):
    if isinstance(employees, str):
        employees = json.loads(employees)
        print("Employees: ", employees)

    count = 0
    for emp_row in employees:
        # Avoid creating duplicate objects if the user clicks multiple times
        checkin = frappe.new_doc("Employee Checkin")
        checkin.employee = emp_row.get("employee")
        checkin.log_type = log_type
        checkin.time = time
        checkin.shift = emp_row.get("shift")
        checkin.insert(ignore_permissions=True)
        count += 1
        
    # Commit changes to database
    frappe.db.commit()
    
    return {"success": True, "count": count}