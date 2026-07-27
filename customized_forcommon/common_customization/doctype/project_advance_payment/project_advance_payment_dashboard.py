from frappe import _
def get_data():
    return {
        # Parent-level field on Payment Entry that links back to Project Advance Payment
        "fieldname": "custom_project_advance_payment",
        "transactions": [
            {
                "label": _("Payment for Project Advance"),
                "items": ["Payment Entry"],
                
            },
            {
                "label": _("Payment Term Invoice"),
                "items": ["Purchase Invoice",],
            },
        ],
    }