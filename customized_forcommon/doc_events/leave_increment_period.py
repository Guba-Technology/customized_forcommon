import frappe

def validate_leave_increment_period(doc, method):
    # Get the leave increment period from the current Employee document
    leave_increment_period = doc.custom_leave_increment_period

    # Validate the value
    if leave_increment_period is not None and leave_increment_period < 0:
        frappe.throw("Leave Increment Period cannot be negative")