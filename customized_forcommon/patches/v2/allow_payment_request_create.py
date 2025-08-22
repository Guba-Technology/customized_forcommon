import frappe

def execute():
    # Fetch the Payment Request 
    doc = frappe.get_doc("DocType", "Payment Request")
    doc.in_create = 0
    doc.save()
    
    frappe.db.commit() 
