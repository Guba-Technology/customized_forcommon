import frappe
from frappe.utils import today, add_days
def check_overdue_invoice():
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "docstatus": 1,
            "outstanding_amount": [">", 0],
            "due_date": ['<', today]
        },
        fields=["name", "posting_date", "customer", "due_date", "outstanding_amount"]
    )
    rules = frappe.get_all(
        "Dunning Rule",
        filters = {},
        fields=[
            "after_days",
            "dunning_fee",
            "dunning_percentage",
            "dunning_based_on",
            "dunning_on"
        ],
    )
    today_date = today()
    for inv in invoices:
        pass

