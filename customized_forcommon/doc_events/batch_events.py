import frappe

def before_insert_batch(doc, method):
    if doc.reference_doctype == "Purchase Receipt" and doc.reference_name:
        pr = frappe.get_doc("Purchase Receipt", doc.reference_name)
        doc.manufacturing_date = pr.posting_date
