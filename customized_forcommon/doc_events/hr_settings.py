import frappe

def validate_severance_starting_year(doc, method):
    severance_starting_year = doc.custom_severenace_pay_starting_year
    if severance_starting_year < 1:
        frappe.throw("Severenace Pay Starting Year cannot be less than 1")