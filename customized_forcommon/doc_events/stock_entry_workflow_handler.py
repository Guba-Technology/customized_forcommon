import frappe
from customized_forcommon.api import send_to_transit, complete_transfer

def check_workflow_state(doc, method):
    if doc.stock_entry_type != "Material Transfer":
        return

    # Draft → Pending Receipt
    if doc.custom_transfer_status == "Pending Receipt":
        send_to_transit(doc.name)

    # Pending Receipt → Completed
    elif doc.custom_transfer_status == "Completed":
        complete_transfer(doc.name)
