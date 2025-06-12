import frappe

def execute():
    # Option 1: Disable the standard report
    if frappe.db.exists("Report", "Job Card Summary"):
        frappe.db.set_value("Report", "Job Card Summary", "disabled", 1)