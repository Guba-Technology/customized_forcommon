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

# Moneky path the bank reconcillation statement
import erpnext.accounts.report.bank_reconciliation_statement.bank_reconciliation_statement as brs
from customized_forcommon.overrides.reports import custom_bank_reconciliation_statement as cb

# Force the override at the moment the app loads
brs.execute = cb.execute

# Purchase Analytics:
import erpnext.buying.report.purchase_analytics.purchase_analytics as pa
from customized_forcommon.overrides.reports import custom_purchase_analytics as cpa

# Force override at app load
pa.execute = cpa.execute


# Purchase Order Analysis monkey patch
import erpnext.buying.report.purchase_order_analysis.purchase_order_analysis as poa
from customized_forcommon.overrides.reports import custom_purchase_order_analysis as cpoa
    
poa.execute = cpoa.execute
poa.get_data = cpoa.get_data
poa.get_columns = cpoa.get_columns
poa.prepare_data = cpoa.prepare_data
poa.update_received_amount = cpoa.update_received_amount
poa.get_received_amount_data = cpoa.get_received_amount_data
poa.prepare_chart_data = cpoa.prepare_chart_data
poa.validate_filters = cpoa.validate_filters


# Monkey patch Fixed Asset Register chart
import erpnext.assets.report.fixed_asset_register.fixed_asset_register as far
from customized_forcommon.overrides.reports import fixed_asset_register as cfar

# Only override the unsafe chart function
far.prepare_chart_data = cfar.prepare_chart_data