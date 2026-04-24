import frappe

def update_linked_purchase_orders(doc, method):
    if not doc.custom_lc_number:
        return

    lc_name = doc.custom_lc_number

    # prevent duplicates
    if frappe.db.exists(
        "LC Purchase Order Table",
        {
            "parent": lc_name,
            "purchase_order": doc.name
        }
    ):
        return

    # Insert into the child table
    child = frappe.get_doc({
        "doctype": "LC Purchase Order Table",
        "parent": lc_name,
        "parenttype": "LC Master",
        "parentfield": "linked_purchase_orders",

        "purchase_order": doc.name,
    })

    child.insert(ignore_permissions=True)
    link = f"<a href='/app/lc-master/{lc_name}'>{lc_name}</a>"
    frappe.msgprint(f"This document detail is added to linked purchase orders table of LC Master <b>{link}</b>")

def remove_linked_purchase_orders(doc, method):
    if not doc.custom_lc_number:
        return

    frappe.db.delete(
        "LC Purchase Order Table",
        {
            "parent": doc.custom_lc_number,
            "purchase_order": doc.name
        }
    )
    link = f"<a href='/app/lc-master/{doc.custom_lc_number}'>{doc.custom_lc_number}</a>"
    frappe.msgprint(f"This document detail is removed from linked purchase orders table of LC Master <b>{link}</b> ")


def update_linked_purchase_invoices(doc, method):
    if not doc.custom_lc_number:
        return

    lc_name = doc.custom_lc_number

    # prevent duplicates
    if frappe.db.exists(
        "LC Purchase Invoice Table",
        {
            "parent": lc_name,
            "purchase_invoice": doc.name
        }
    ):
        return

    # Insert into the child table
    child = frappe.get_doc({
        "doctype": "LC Purchase Invoice Table",
        "parent": lc_name,
        "parenttype": "LC Master",
        "parentfield": "linked_purchase_invoices",

        "purchase_invoice": doc.name,
    })

    child.insert(ignore_permissions=True)
    link = f"<a href='/app/lc-master/{lc_name}'>{lc_name}</a>"
    frappe.msgprint(f"This document detail is added to linked purchase invoices table of LC Master <b>{link}</b>")

def remove_linked_purchase_invoices(doc, method):
    if not doc.custom_lc_number:
        return

    frappe.db.delete(
        "LC Purchase Invoice Table",
        {
            "parent": doc.custom_lc_number,
            "purchase_invoice": doc.name
        }
    )
    link = f"<a href='/app/lc-master/{doc.custom_lc_number}'>{doc.custom_lc_number}</a>"
    frappe.msgprint(f"This document detail is removed from linked purchase invoices table of LC Master <b>{link}</b> ")



def update_linked_purchase_receipts(doc, method):
    if not doc.custom_lc_number:
        return

    lc_name = doc.custom_lc_number

    # prevent duplicates
    if frappe.db.exists(
        "LC Purchase Receipt Table",
        {
            "parent": lc_name,
            "purchase_receipt": doc.name
        }
    ):
        return

    # Insert into the child table
    child = frappe.get_doc({
        "doctype": "LC Purchase Receipt Table",
        "parent": lc_name,
        "parenttype": "LC Master",
        "parentfield": "linked_purchase_receipts",

        "receipt_number": doc.name,
    })

    child.insert(ignore_permissions=True)
    link = f"<a href='/app/lc-master/{lc_name}'>{lc_name}</a>"
    frappe.msgprint(f"This document detail is added to linked purchase receipts table of LC Master <b>{link}</b>")

def remove_linked_purchase_receipts(doc, method):
    if not doc.custom_lc_number:
        return

    frappe.db.delete(
        "LC Purchase Receipt Table",
        {
            "parent": doc.custom_lc_number,
            "receipt_number": doc.name
        }
    )
    link = f"<a href='/app/lc-master/{doc.custom_lc_number}'>{doc.custom_lc_number}</a>"
    frappe.msgprint(f"This document detail is removed from linked purchase receipts table of LC Master <b>{link}</b> ")

def update_linked_payment_entries(doc, method):
    if not doc.custom_lc_number or not doc.party_type == "Supplier":
        return

    lc_name = doc.custom_lc_number

    # prevent duplicates
    if frappe.db.exists(
        "LC Payment Entry Table",
        {
            "parent": lc_name,
            "payment_entry": doc.name
        }
    ):
        return

    # Insert into the child table
    child = frappe.get_doc({
        "doctype": "LC Payment Entry Table",
        "parent": lc_name,
        "parenttype": "LC Master",
        "parentfield": "linked_payment_entries",

        "payment_entry": doc.name
    })

    child.insert(ignore_permissions=True)
    link = f"<a href='/app/lc-master/{lc_name}'>{lc_name}</a>"
    frappe.msgprint(f"This document detail is added to linked payment entries table of LC Master <b>{link}</b>")

def remove_linked_payment_entries(doc, method):
    if not doc.custom_lc_number:
        return

    frappe.db.delete(
        "LC Payment Entry Table",
        {
            "parent": doc.custom_lc_number,
            "payment_entry": doc.name
        }
    )
    link = f"<a href='/app/lc-master/{doc.custom_lc_number}'>{doc.custom_lc_number}</a>"
    frappe.msgprint(f"This document detail is removed from linked payment entries table of LC Master <b>{link}</b> ")


def update_linked_journal_entries(doc, method):
    if not doc.custom_lc_number:
        return

    lc_name = doc.custom_lc_number

    # prevent duplicates
    if frappe.db.exists(
        "LC Journal Entry Table",
        {
            "parent": lc_name,
            "payment_entry": doc.name
        }
    ):
        return

    # Insert into the child table
    child = frappe.get_doc({
        "doctype": "LC Journal Entry Table",
        "parent": lc_name,
        "parenttype": "LC Master",
        "parentfield": "linked_journal_entries",

        "journal_entry": doc.name,
    })

    child.insert(ignore_permissions=True)
    link = f"<a href='/app/lc-master/{lc_name}'>{lc_name}</a>"
    frappe.msgprint(f"This document detail is added to linked journal entries table of LC Master <b>{link}</b>")

def remove_linked_journal_entries(doc, method):
    if not doc.custom_lc_number:
        return

    frappe.db.delete(
        "LC Journal Entry Table",
        {
            "parent": doc.custom_lc_number,
            "journal_entry": doc.name
        }
    )
    link = f"<a href='/app/lc-master/{doc.custom_lc_number}'>{doc.custom_lc_number}</a>"
    frappe.msgprint(f"This document detail is removed from linked journal entries table of LC Master <b>{link}</b> ")

def update_allocated_amount(doc, method):
    if not doc.references or doc.party_type != "Supplier":
        return

    for ref in doc.references:

        allocated = ref.allocated_amount or 0
        if not allocated:
            continue

        if ref.reference_doctype == "Purchase Order":

            po_name = ref.reference_name

            lc_name = frappe.db.get_value(
                "Purchase Order",
                po_name,
                "custom_lc_number"
            )
            if not lc_name:
                continue

            row = frappe.db.get_value(
                "LC Purchase Order Table",
                {
                    "parent": lc_name,
                    "purchase_order": po_name
                },
                ["name", "allocated"],
                as_dict=True
            )
            if not row:
                continue

            new_allocated = (row.allocated or 0) + allocated

            frappe.db.set_value(
                "LC Purchase Order Table",
                row.name,
                "allocated",
                new_allocated
            )

        elif ref.reference_doctype == "Purchase Invoice":

            pi_name = ref.reference_name

            lc_name = frappe.db.get_value(
                "Purchase Invoice",
                pi_name,
                "custom_lc_number"
            )
            if not lc_name:
                continue

            row = frappe.db.get_value(
                "LC Purchase Invoice Table",
                {
                    "parent": lc_name,
                    "purchase_invoice": pi_name
                },
                ["name", "allocated"],
                as_dict=True
            )
            if not row:
                continue

            new_allocated = (row.allocated or 0) + allocated

            frappe.db.set_value(
                "LC Purchase Invoice Table",
                row.name,
                "allocated",
                new_allocated
            )

def reverse_allocated_amount(doc, method):
    if not doc.references or doc.party_type != "Supplier":
        return

    for ref in doc.references:

        allocated = ref.allocated_amount or 0
        if not allocated:
            continue

        if ref.reference_doctype == "Purchase Order":

            po_name = ref.reference_name

            lc_name = frappe.db.get_value(
                "Purchase Order",
                po_name,
                "custom_lc_number"
            )
            if not lc_name:
                continue

            row = frappe.db.get_value(
                "LC Purchase Order Table",
                {
                    "parent": lc_name,
                    "purchase_order": po_name
                },
                ["name", "allocated"],
                as_dict=True
            )
            if not row:
                continue

            frappe.db.set_value(
                "LC Purchase Order Table",
                row.name,
                "allocated",
                (row.allocated or 0) - allocated
            )

        elif ref.reference_doctype == "Purchase Invoice":

            pi_name = ref.reference_name

            lc_name = frappe.db.get_value(
                "Purchase Invoice",
                pi_name,
                "custom_lc_number"
            )
            if not lc_name:
                continue

            row = frappe.db.get_value(
                "LC Purchase Invoice Table",
                {
                    "parent": lc_name,
                    "purchase_invoice": pi_name
                },
                ["name", "allocated"],
                as_dict=True
            )
            if not row:
                continue

            frappe.db.set_value(
                "LC Purchase Invoice Table",
                row.name,
                "allocated",
                (row.allocated or 0) - allocated
            )