import frappe
from frappe.utils import today, getdate

def execute():
    customers = frappe.get_all("Customer", fields=['name', 'disabled', 'custom_license_expiry_date'])
    today_date = getdate(today())
    
    for customer in customers:
        expiry_date = getdate(customer.custom_license_expiry_date) if customer.custom_license_expiry_date else None
        if expiry_date and expiry_date < today_date:
            frappe.db.set_value("Customer", customer.name, "disabled", 1)

    frappe.db.commit()
