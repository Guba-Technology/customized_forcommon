import frappe

def execute():
    field_name = "Stock Entry-cost_center2"
    depends_condition = "eval:['Material Issue','Material Receipt'].includes(doc.stock_entry_type)"

    if frappe.db.exists("Custom Field", field_name):
        # Update existing field
        frappe.db.set_value(
            "Custom Field",
            field_name,
            "depends_on",
            depends_condition
        )
    else:
        # Create field if it doesn't exist
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Stock Entry",
            "fieldname": "cost_center2",
            "label": "Cost Center",
            "fieldtype": "Link",
            "options": "Cost Center",
            "insert_after": "scan_barcode",
            "depends_on": depends_condition,
            "allow_on_submit": 1
        }).insert(ignore_permissions=True)

    frappe.clear_cache()