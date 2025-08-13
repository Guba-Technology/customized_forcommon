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

        if frappe.db.exists("Workspace", new_name):
            # New name already exists, remove the old one to avoid duplicates
            frappe.delete_doc("Workspace", old_name, force=True)
        else:
            # New name doesn't exist, so rename old to new
            frappe.rename_doc("Workspace", old_name, new_name, force=True)
            frappe.db.set_value("Workspace", new_name, "title", new_name)

    frappe.db.commit()
