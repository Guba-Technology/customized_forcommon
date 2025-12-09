import frappe
from frappe.utils import today, getdate

def validate_license_dates(doc, method):
    issue_date = getdate(doc.custom_license_issue_date)
    expiry_date = getdate(doc.custom_license_expiry_date)

    if expiry_date == issue_date:
        frappe.throw("License issue date cannot be the same with license expiry date")
    elif expiry_date < issue_date:
        frappe.throw("License issue date cannot be after license expiry date")