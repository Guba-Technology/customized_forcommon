import frappe
def validate_leave_increment_period(doc, method):
    leave_increment_period = frappe.db.get_value("Employee", "custom_leave_increment_period")
    if leave_increment_period < 0:
        frappe.throw("Leave Increment Period cannot be negative")