import frappe

def execute():

    # 1️⃣ Shelf Number (Item)
    if not frappe.db.exists("Custom Field", {"dt": "Item", "fieldname": "shelf_number"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Item",
            "label": "Shelf Number",
            "fieldname": "shelf_number",
            "fieldtype": "Data",
            "insert_after": "stock_uom",
            "read_only": 0,
            "default": "SNO-",
            "unique": True
        }).insert(ignore_permissions=True)

    # 2️⃣ Item End Date on Purchase Receipt
    if not frappe.db.exists("Custom Field", {"dt": "Purchase Receipt", "fieldname": "item_end_date"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Purchase Receipt",
            "label": "Item End Date",
            "fieldname": "item_end_date",
            "fieldtype": "Date",
            "insert_after": "posting_date",
        }).insert(ignore_permissions=True)

    # 3️⃣ Item Status (Item)
    if not frappe.db.exists("Custom Field", {"dt": "Item", "fieldname": "item_status"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Item",
            "label": "Item Status",
            "fieldname": "item_status",
            "fieldtype": "Select",
            "options": "Active\nBorrowed\nExpired",
            "insert_after": "shelf_number",
            "default": "Active",
            "read_only": 1
        }).insert(ignore_permissions=True)

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
