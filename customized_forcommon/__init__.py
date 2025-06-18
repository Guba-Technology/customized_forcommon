__version__ = "0.0.1"

def override_core_delete_check():
	import frappe.model.delete_doc
	from customized_forcommon.overrides.delete_check import custom_check_permission_and_not_submitted

	# Monkey patch the original method
	frappe.model.delete_doc.check_permission_and_not_submitted = custom_check_permission_and_not_submitted


def override_navbar():
    import frappe.utils.install
    from customized_forcommon.overrides.navbar_patch import custom_add_standard_navbar_items
    frappe.utils.install.add_standard_navbar_items = custom_add_standard_navbar_items

override_navbar()
override_core_delete_check()

