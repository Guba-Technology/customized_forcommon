import frappe

def execute():
    workspace_renames = {
        "Selling": "Sales and Marketing",
        "Assets": "Fixed Assets",
        "HR": "Human Resource",
        "Buying": "Procurement",
        "Stock": "Inventory",
        "ERPNext Settings": "ERP Settings",
        "ERPNext Integrations": "ERP Integrations",
        # Add more as needed
    }

    for old_name, new_name in workspace_renames.items():
        # Check if the old workspace exists
        if frappe.db.exists("Workspace", old_name):
            # If the new name already exists, delete it first
            if frappe.db.exists("Workspace", new_name):
                frappe.delete_doc("Workspace", new_name, force=True)

            # Rename the workspace
            frappe.rename_doc("Workspace", old_name, new_name, force=True)
            # Update the title if needed
            frappe.db.set_value("Workspace", new_name, "title", new_name)
