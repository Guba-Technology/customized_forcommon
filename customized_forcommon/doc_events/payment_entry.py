import frappe

def set_advance_paid_in_project_advance_payment(doc, method):
    if not doc.custom_project_advance_payment:
        return
    frappe.db.set_value("Project Advance Payment", doc.custom_project_advance_payment, 
                        {
                            "advance_paid":1,
                            "created_advance_payment_entry": doc.name
                         }
                        )



def unset_advance_paid_in_project_advance_payment(doc, method):
    if not doc.custom_project_advance_payment:
        return
    frappe.db.set_value("Project Advance Payment", doc.custom_project_advance_payment, 
                            {
                                "advance_paid":0,
                                "created_advance_payment_entry": None,
                             }
                            )

def set_payment_entry_in_project_advance_payment(doc, method):
    for row in doc.references:
        if not row.reference_doctype == "Purchase Invoice":
            return

        status = frappe.db.get_value("Purchase Invoice", row.reference_name, "status")
        pap = frappe.db.get_value("Purchase Invoice", row.reference_name, "custom_project_advance_payment")
        
        if not pap:
            return

        row = frappe.get_all(
                "Advance Recovery Detail",
                filters={
                    "parent": pap,
                    "invoice": row.reference_name
                },
                fields=["name"],
                limit=1
            )
        if row:
                frappe.db.set_value(
                    "Advance Recovery Detail",
                    row[0].name,
                    {
                        "payment_entry": doc.name,
                        "invoice_status": status
                    }
                )
        
def unset_payment_entry_in_project_advance_payment(doc, method):
    for row in doc.references:
        if not row.reference_doctype == "Purchase Invoice":
            return

        status = frappe.db.get_value("Purchase Invoice", row.reference_name, "status")
        pap = frappe.db.get_value("Purchase Invoice", row.reference_name, "custom_project_advance_payment")

        if not pap:
            return
            
        row = frappe.get_all(
                "Advance Recovery Detail",
                filters={
                    "parent": pap,
                    "invoice": row.reference_name
                },
                fields=["name"],
                limit=1
            )
        if row:
                frappe.db.set_value(
                    "Advance Recovery Detail",
                    row[0].name,
                    {
                        "payment_entry": None,
                        "invoice_status": status
                    }
                )
        
