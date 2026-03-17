import frappe
def update_fuel_payment(doc, method):
    fuel_price = frappe.db.get_value("Company", doc.company, "custom_fuel_price")
    if doc.custom_allowed_fuel > 0 and fuel_price > 0:
        doc.custom_fuel_payment = doc.custom_allowed_fuel * fuel_price
