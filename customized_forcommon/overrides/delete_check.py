import frappe
from frappe import _
from frappe.exceptions import PermissionError

def custom_check_permission_and_not_submitted(doc):
	# Permission check
	if (
		not doc.flags.ignore_permissions
		and frappe.session.user != "Administrator"
		and (not doc.has_permission("delete") or (doc.doctype == "DocType" and not doc.custom))
	):
		frappe.msgprint(
			_("User not allowed to delete {0}: {1}").format(doc.doctype, doc.name),
			raise_exception=PermissionError,
		)

	# Check if submitted
	if doc.meta.is_submittable and doc.docstatus.is_submitted():
		frappe.msgprint(
			_("{0} {1}: You Cannot delete submitted record. Please cancel it first.").format(
				_(doc.doctype), doc.name
			),
			raise_exception=True,
		)
