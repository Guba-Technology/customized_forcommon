import frappe

def calculate_total_factory_share(doc, method):
    total_factory_share = 0
    if doc.items:
        for item in doc.items:
            factory_share_amount = frappe.db.get_value("Item", item, "custom_factory_share_amount")
            total_factory_share += factory_share_amount * item.qty
        doc.custom_factory_share_total = total_factory_share 

def calculate_tax_amount_for_factory_share(doc, method):
    total = 0
    for tax in doc.get("taxes", []):
        if tax.charge_type == "On Factory Share":
            tax.tax_amount =  doc.custom_factory_share_total * tax.rate / 100
            tax.total =  doc.custom_factory_share_total  + tax.tax_amount
        total +=  tax.total
    doc.base_total_taxes_and_charges = total
    doc.total_taxes_and_charges = total

def calculate_tax_amount_for_sidf(doc, method):
    total = 0
    for tax in doc.get("taxes", []):
        if tax.charge_type == "SIDF":
           tax.rate = 0
           tax.tax_amount =   doc.total - doc.custom_factory_share_total
           tax.total =  tax.tax_amount
        total +=  tax.total
    doc.base_total_taxes_and_charges = total
    doc.total_taxes_and_charges = total
   
def block_factory_share_and_sidf(doc, method):
    for tax in doc.get("taxes", []):
        if tax.charge_type == "On Factory Share":
            frappe.throw("On Factory Share is only allowed for Sales Invoice and Sales Order")
        if  tax.charge_type ==  tax.charge_type == "SIDF":
             frappe.throw("SIDF is only allowed for Sales Invoice and Sales Order")