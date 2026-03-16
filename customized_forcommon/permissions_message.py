import frappe
from frappe import _

def custom_permission_message():
    exc = frappe.local.message_log
    if exc:
        for m in exc:
            if "Not permitted" in str(m):
                frappe.clear_messages()
                frappe.throw(
                    _("You do not have permission to access this document. Please contact the administrator."),
                    frappe.PermissionError
                )