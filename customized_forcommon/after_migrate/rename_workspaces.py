import frappe

def run():
    workspace_renames = {
        "Selling": "Sales and Marketing",
        "Assets": "Fixed Assets",
        "HR": "Human Resource",
        "Buying": "Procurement",
        "Stock": "Inventory",
        "ERPNext Settings": "ERP Settings",
        "ERPNext Integrations": "ERP Integrations",
    }

    for old_name, new_name in workspace_renames.items():
        if not frappe.db.exists("Workspace", old_name):
            continue

        # If the target workspace exists, skip the rename to preserve fixtures
        if frappe.db.exists("Workspace", new_name):
            continue

        frappe.rename_doc("Workspace", old_name, new_name, force=True)
        frappe.db.set_value("Workspace", new_name, "title", new_name)

    frappe.db.commit()
