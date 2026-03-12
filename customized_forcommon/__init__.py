__version__ = "0.0.1"

def override_core_delete_check():
	import frappe.model.delete_doc
	from customized_forcommon.overrides.delete_check import custom_check_permission_and_not_submitted

	# Monkey patch the original method
	frappe.model.delete_doc.check_permission_and_not_submitted = custom_check_permission_and_not_submitted

override_core_delete_check()

# Moneky path the bank reconcillation statement
import erpnext.accounts.report.bank_reconciliation_statement.bank_reconciliation_statement as brs
from customized_forcommon.overrides.reports import custom_bank_reconciliation_statement as cb

# Force the override at the moment the app loads
brs.execute = cb.execute