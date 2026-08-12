import frappe
from frappe import _

def validate_more_than_one_cash_component(doc, method):
    # Only validate if the current component is ENABLED and marked as a CASH COMPONENT
    if not doc.enabled or not doc.get("custom_is_component_for_cash"):
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