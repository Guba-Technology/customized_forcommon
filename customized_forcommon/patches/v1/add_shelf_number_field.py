import frappe

def execute():

    # 4️⃣ Expired Warehouse (Stock Settings)
    if not frappe.db.exists("Custom Field", {"dt": "Stock Settings", "fieldname": "expired_warehouse"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Stock Settings",
            "label": "Expired Warehouse",
            "fieldname": "expired_warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "insert_after": "default_warehouse"
        }).insert(ignore_permissions=True)

    frappe.db.commit()
