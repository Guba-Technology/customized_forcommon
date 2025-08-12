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
            frappe.delete_doc("Workspace", new_name, force=True)

        frappe.rename_doc("Workspace", old_name, new_name, force=True)
        frappe.db.set_value("Workspace", new_name, "title", new_name)

    # ✅ Ensure Maintenance Request link exists after rename
    ws = frappe.get_doc("Workspace", "Fixed Assets")
    if not any(l.link_to == "Maintenance Request" for l in ws.links):
        ws.append("links", {
            "label": "Maintenance Request",
            "link_to": "Maintenance Request",
            "link_type": "DocType",
            "hidden": 0
        })
        ws.save(ignore_permissions=True)

    frappe.db.commit()
