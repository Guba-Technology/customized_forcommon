import frappe

def custom_before_submit(doc, method):
    """
    Custom logic for inter-branch transfer
    """
    if doc.purpose != "Material Transfer":
        return

    if doc.custom_transfer_status == "Pending Receipt":
        # Only deduct from source warehouse
        for item in doc.items:
            item.t_warehouse = None  # prevent adding to target
        frappe.msgprint("Stock will be deducted from Source Warehouse only. Await Target confirmation.")

    elif doc.custom_transfer_status == "Completed":
        # Only add to target warehouse
        for item in doc.items:
            item.s_warehouse = None  # prevent deduction from source again
        frappe.msgprint("Stock will be added to Target Warehouse. Transfer completed.")
