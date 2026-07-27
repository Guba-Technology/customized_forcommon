import frappe

def set_created_invoice_and_recovery_details_in_project_advance_payment_terms(doc, method):
    if not (doc.custom_project_advance_payment and doc.custom_project_advance_payment_term):
        return

    row = frappe.get_all(
        "Project Advance Payment Terms",
        filters={
            "parent": doc.custom_project_advance_payment,
            "payment_term": doc.custom_project_advance_payment_term
        },
        fields=["name"],
        limit=1
    )

    if row:
        frappe.db.set_value(
            "Project Advance Payment Terms",
            row[0].name,
            {
                "created_purchase_invoice": doc.name,
                "invoice_created": 1
            }
        )
    
    total = doc.grand_total or 0
    advance_percent = frappe.db.get_value("Project Advance Payment", doc.custom_project_advance_payment, "advance_percent")
    
    recovered_amount = (total * advance_percent / 100) if advance_percent > 0 else 0
    net_paid = total - recovered_amount
    child = frappe.get_doc({
        "doctype": "Advance Recovery Detail",
        "parent": doc.custom_project_advance_payment,
        "parenttype": "Project Advance Payment",
        "parentfield": "recovery_details",
        "invoice": doc.name,
        "recovered_amount": recovered_amount,
        "net_paid": net_paid,
    })
    child.insert()


def unset_created_invoice_and_recovery_details_in_project_advance_payment_terms(doc, method):
    if not (doc.custom_project_advance_payment and doc.custom_project_advance_payment_term):
        return
    row = frappe.get_all(
        "Project Advance Payment Terms",
        filters={
            "parent": doc.custom_project_advance_payment,
            "payment_term": doc.custom_project_advance_payment_term
        },
        fields=["name"],
        limit=1
    )

    if row:
        frappe.db.set_value(
            "Project Advance Payment Terms",
            row[0].name,
            {
                "created_purchase_invoice": None,
                "invoice_created": 0
            }
        )

    recovery_rows = frappe.get_all(
        "Advance Recovery Detail",
        filters={
            "parent": doc.custom_project_advance_payment,
            "parenttype": "Project Advance Payment",
            "parentfield": "recovery_details",
            "invoice": doc.name
        },
        fields=["name"]
    )

    for recovery in recovery_rows:
        frappe.delete_doc(
            "Advance Recovery Detail",
            recovery.name
        )
    frappe.db.commit()
    