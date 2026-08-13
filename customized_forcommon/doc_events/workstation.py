import frappe

def calculate_hour_rate(doc, method):
    if doc.custom_cost_components:
        #fetch all costs from the child table-custom_cost_components and calculate the total cost
        total_cost = sum([row.operating_cost for row in doc.custom_cost_components])
        doc.hour_rate = total_cost
    else:
        doc.hour_rate = 0.0