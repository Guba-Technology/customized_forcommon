import frappe
from frappe import _
from customized_forcommon.api import send_to_transit, complete_transfer

def check_workflow_state(doc, method):
    """
    Handle workflow transitions for Stock Entry (Material Transfer only).
    Calls appropriate whitelisted methods to create Stock Ledger Entries.
    """

    if doc.doctype != "Stock Entry" or doc.stock_entry_type != "Material Transfer":
        return

    # Draft → Pending Receipt
    if doc.custom_transfer_status == "Pending Receipt":
        frappe.msgprint(_("Workflow moved to Pending Receipt. Executing send_to_transit..."))
        send_to_transit(doc.name)

    # Pending Receipt → Completed
    elif doc.custom_transfer_status == "Completed":
        frappe.msgprint(_("Workflow moved to Completed. Executing complete_transfer..."))
        complete_transfer(doc.name)
