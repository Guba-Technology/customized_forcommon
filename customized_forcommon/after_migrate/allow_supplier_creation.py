import frappe

def execute():
    frappe.db.set_value("DocType", "Supplier", "in_create", 0)
    frappe.clear_cache(doctype="Supplier")