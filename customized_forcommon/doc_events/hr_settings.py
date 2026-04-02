import frappe
from customized_forcommon.api import calculate_severance_amount

def validate_severance_starting_year(doc, method):
    severance_starting_year = doc.custom_severenace_pay_starting_year
    if severance_starting_year < 1:
        frappe.throw("Severenace Pay Starting Year cannot be less than 1")

def update_employee_severance_pay_amount(doc, method):
    if not doc.has_value_changed("custom_severenace_pay_starting_year"):
        return

    employees = frappe.get_all(
        "Employee",
        filters={
            "status": "Active",
            "custom_apply_severance_pay": 1,
            "relieving_date": ["is", "set"],
            "date_of_joining": ["is", "set"]
        },
        fields=["name"]
    )

    for emp in employees:
        emp_doc = frappe.get_doc("Employee", emp.name)

        severance = calculate_severance_amount(emp_doc)

        frappe.db.set_value(
            "Employee",
            emp_doc.name,
            "custom_severance_pay_amount",
            severance
        )
