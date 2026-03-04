from frappe import _

def get_data(data):
    # Add the custom field mapping
    data["non_standard_fieldnames"]["Employee Advance"] = "custom_purchase_order_id"
    
    # Add Employee Advance to the 'Payment' transaction group
    for section in data["transactions"]:
        if section["label"] == _("Payment"):
            if "Employee Advance" not in section["items"]:
                section["items"].append("Employee Advance")
    
    return data