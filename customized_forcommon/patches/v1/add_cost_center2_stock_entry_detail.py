import frappe

def execute():
    if not frappe.db.exists("Custom Field", "Stock Entry-cost_center2"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Stock Entry",
            "fieldname": "cost_center2",
            "label": "Cost Center",
            "fieldtype": "Link",
            "options": "Cost Center",
            "insert_after": "scan_barcode",
            "depends_on": "eval:doc.stock_entry_type=='Material Issue'",
            "allow_on_submit": 1
        }).insert(ignore_permissions=True)

    frappe.clear_cache()
