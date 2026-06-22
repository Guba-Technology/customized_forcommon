import frappe

def execute():
    if not frappe.db.exists("Stock Entry Type", "Material Return"):
        doc = frappe.get_doc({
            "doctype": "Stock Entry Type",
            "name": "Material Return",
            "purpose": "Material Receipt",
            "is_standard": 0
        })
        doc.insert(ignore_permissions=True)