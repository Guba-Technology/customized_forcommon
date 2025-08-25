import frappe
from customized_forcommon.api import send_to_transit, complete_transfer

def stock_entry_workflow_handler(doc, method):
    if doc.stock_entry_type != "Material Transfer":
        return

    # Check the workflow action just performed
    workflow_state = doc.custom_transfer_status

    if workflow_state == "Pending Receipt":
        # Draft → Pending Receipt
        send_to_transit(doc.name)

    elif workflow_state == "Completed":
        # Pending Receipt → Completed
        complete_transfer(doc.name)
