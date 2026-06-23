import frappe
from frappe import _


def get_data():
    data = {
       "non_standard_fieldnames":{
           "Employee Transfer": "employee",
           "Employee Promotion": "employee"
       },
       "transactions": [
                {
                    "label": _("Connections"),
                    "items": [
                        "Employee Promotion",
                        "Employee Transfer",
                    
                    ]
                }           
            ],
            "transactions_label": {
                "Employee Promotion": _("Employee Promotion"),
                "Employee Transfer": _("Employee Transfer"),
              
            }
    }
    return data