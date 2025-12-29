import frappe
from frappe import _
def get_data():
    return {
      		"fieldname": "custom_talent_management_reference",
            "transactions": [
                {
                    "label": _("Connections"),
                    "items": [
                        "Employee Promotion",
                        "Employee Transfer",
                        "Employee Onboarding",
                        "Employee Incentive"
                    ]
                }           
            ],
            "transactions_label": {
                "Employee Promotion": _("Employee Promotion"),
                "Employee Transfer": _("Employee Transfer"),
                "Employee Onboarding": _("Employee Onboarding"),
                "Employee Incentive": _("Employee Incentive")
            }


    }