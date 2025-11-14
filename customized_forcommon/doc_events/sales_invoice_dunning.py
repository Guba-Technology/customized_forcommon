import frappe

def calculate_dunning_fee(doc, method):
    if doc.custom_dunning_rule:
        for row in doc.custom_dunning_rule:
            if row.dunning_based_on == "Percentage":
                if row.dunning_percentage <= 0.0:
                    frappe.throw("Dunning Percentage cannot be less than or equals to 0!")
                if row.dunning_percentage:
                    if row.dunning_on == "VAT Inclusive":
                        row.dunning_fee = doc.grand_total * row.dunning_percentage / 100
                    elif row.dunning_on == "VAT Exclusive":
                        row.dunning_fee = doc.total * row.dunning_percentage / 100
            else:
                # If not percentage based, reset dunning_percentage
                row.dunning_percentage = 0
