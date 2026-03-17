import frappe
from frappe import _

def custom_permission_message(doc, ptype, user=None, debug=False):
    user = user or frappe.session.user

    if not frappe.has_permission(doc.doctype, ptype, user=user):
        frappe.throw(
            _("You do not have permission to access document {1}.Please contact the administrator.").format(
                frappe.bold(user),
                frappe.bold(f"{doc.doctype}: {doc.name}")
            ),
            frappe.PermissionError
        )