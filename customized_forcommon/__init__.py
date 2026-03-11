__version__ = "0.0.1"

def override_core_delete_check():
	import frappe.model.delete_doc
	from customized_forcommon.overrides.delete_check import custom_check_permission_and_not_submitted

	# Monkey patch the original method
	frappe.model.delete_doc.check_permission_and_not_submitted = custom_check_permission_and_not_submitted

override_core_delete_check()

# customized_forcommon/overrides/__init__.py

def override_bom_creator():
    import erpnext.manufacturing.doctype.bom_creator.bom_creator as bom_creator
    from customized_forcommon.overrides.bom_creator import get_children, add_sub_assembly

    # Patch safely
    bom_creator.get_children = get_children
    bom_creator.add_sub_assembly = add_sub_assembly
    
override_bom_creator()


import erpnext.accounts.report.bank_reconciliation_statement.bank_reconciliation_statement as brs
from customized_forcommon.overrides.reports import custom_bank_reconciliation_statement as cb

# Force the override at the moment the app loads
brs.execute = cb.execute