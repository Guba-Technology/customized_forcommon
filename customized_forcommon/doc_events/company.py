import frappe

def update_employee_fuel_price(doc, method):
    if not doc.has_value_changed("custom_fuel_price"):
        return

    employees = frappe.get_all(
        "Employee",
        filters={"company": doc.name},
        fields=["name", "custom_allowed_fuel"]
    )

    for emp in employees:
        total_fuel_amount = (emp.custom_allowed_fuel or 0) * (doc.custom_fuel_price or 0)
        if emp.custom_allowed_fuel > 0:
            frappe.db.set_value(
                "Employee",
                emp.name,
                "custom_fuel_payment",
                total_fuel_amount
            )