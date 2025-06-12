import frappe

def execute():
    field = frappe.get_meta("Employee Advance").get_field("advance_account")
    if field:
        field.fetch_from = None
        frappe.db.commit()
    
