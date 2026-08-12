import frappe
from frappe import _

def calculate_cash_amount(doc, method):
    if not doc.employee or not doc.start_date or not doc.end_date:
        return

    cash_amount = frappe.db.get_value(
        "Salary Payment Distribution Request",
        {
            "employee": doc.employee,
            "company": doc.company,
            "docstatus": 1,
            "effective_from": [">=", doc.start_date],
            "effective_to": ["<=", doc.end_date]
        },
        "cash_amount"
    )
    
    # Defaults to 0.0 if no matching document is found
    doc.custom_cash_amount = cash_amount or 0.0

def validate_more_than_one_cash_component(doc, method):
    # Only validate if the current component is ENABLED and marked as a CASH COMPONENT
    if (doc.disabled == 1) or not doc.get("custom_is_component_for_cash"):
        return

    # Check if ANY OTHER enabled cash component exists
    cash_components = frappe.get_all(
        "Salary Component", 
        filters={
            "name": ["!=", doc.name],
            "disabled": 0,
            "custom_is_component_for_cash": 1
        },
        pluck="name"
    )

    if cash_components:
        frappe.throw(
            _("Another enabled salary component for cash payment already exists: <b>{0}</b>")
            .format(cash_components[0])
        )