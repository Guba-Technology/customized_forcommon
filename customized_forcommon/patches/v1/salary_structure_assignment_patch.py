import frappe

def execute():
    """Force create Property Setter to fetch base from employee.ctc"""
    ps = frappe.get_doc({
        "doctype": "Property Setter",
        "doctype_or_field": "DocField",
        "doc_type": "Salary Structure Assignment",
        "field_name": "base",
        "property": "fetch_from",
        "value": "employee.ctc",
        "property_type": "Data"
    })
    ps.insert(ignore_permissions=True, ignore_if_duplicate=True)
    frappe.db.commit()
