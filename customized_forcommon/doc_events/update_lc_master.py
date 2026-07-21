import frappe

def validate_lc_is_editable(lc_number):
    if not lc_number:
        return

    lc = frappe.db.get_value(
        "LC Master",
        lc_number,
        ["name", "status"],
        as_dict=True
    )

    if not lc:
        return

    if lc.status == "Closed":
        frappe.throw(
            f"LC Master <b>{lc.name}</b> is Closed. "
            "You cannot modify linked documents."
        )

def update_linked_purchase_orders(doc, method):
    if not doc.custom_lc_number:
        return
    
    validate_lc_is_editable(doc.custom_lc_number)

    lc_name = doc.custom_lc_number
    
     # prevent duplicates
    if frappe.db.exists(
        "LC Purchase Order Table",
        {
            "parent": lc_name,
            "purchase_order": doc.name
        }
    ):
        frappe.msgprint(f"Purchase Order {doc.name} is already added in LC Master: {link}")
        return
    lc_master = frappe.get_doc("LC Master", lc_name)
    link = f"<a href='/app/lc-master/{lc_name}'>{lc_name}</a>"
    if lc_master.linked_purchase_orders:
        if len(lc_master.linked_purchase_orders) == 1:
            frappe.msgprint(f"Another Purchase Order is already added in  LC Master: {link}, this will not be added")
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
    frappe.msgprint(f"This document detail is added to linked purchase orders table of LC Master <b>{link}</b>")

def remove_linked_purchase_orders(doc, method):
    if not doc.custom_lc_number:
        return
    validate_lc_is_editable(doc.custom_lc_number)

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
    validate_lc_is_editable(doc.custom_lc_number)

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
    validate_lc_is_editable(doc.custom_lc_number)

    frappe.db.delete(
        "LC Purchase Invoice Table",
        {
            "parent": doc.custom_lc_number,
            "purchase_invoice": doc.name
        }
    )
    link = f"<a href='/app/lc-master/{doc.custom_lc_number}'>{doc.custom_lc_number}</a>"
    frappe.msgprint(f"This document detail is removed from linked purchase invoices table of LC Master <b>{link}</b> ")


def update_lc_purchase_invoice_status_from_payment(doc, method):
    for ref in doc.references:

        if ref.reference_doctype != "Purchase Invoice":
            continue

        invoice = frappe.get_doc(
            "Purchase Invoice",
            ref.reference_name
        )

        # Ensure latest status is loaded
        invoice.reload()

        if not invoice.custom_lc_number:
            continue
        validate_lc_is_editable(invoice.custom_lc_number)

        row_name = frappe.db.get_value(
            "LC Purchase Invoice Table",
            {
                "parent": invoice.custom_lc_number,
                "purchase_invoice": invoice.name
            },
            "name"
        )

        if row_name:
            frappe.db.set_value(
                "LC Purchase Invoice Table",
                row_name,
                "status",
                invoice.status
            )

def update_linked_purchase_receipts(doc, method):
    if not doc.custom_lc_number:
        return
    validate_lc_is_editable(doc.custom_lc_number)

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
    validate_lc_is_editable(doc.custom_lc_number)

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
    validate_lc_is_editable(doc.custom_lc_number)
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
    validate_lc_is_editable(doc.custom_lc_number)

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
    validate_lc_is_editable(doc.custom_lc_number)

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
    validate_lc_is_editable(doc.custom_lc_number)

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
            validate_lc_is_editable(lc_name)

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
            validate_lc_is_editable(lc_name)

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
            validate_lc_is_editable(lc_name)

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


def update_lc_purchase_order_status_from_invoice(doc, method):
    for item in doc.items:
        if not item.purchase_order:
            continue

        purchase_order = frappe.get_doc("Purchase Order", item.purchase_order)

        if not purchase_order.custom_lc_number:
            continue
        validate_lc_is_editable(purchase_order.custom_lc_number)

        row_name = frappe.db.get_value(
            "LC Purchase Order Table",
            {
                "parent": purchase_order.custom_lc_number,
                "purchase_order": purchase_order.name
            },
            "name"
        )

        if row_name:
            frappe.db.set_value(
                "LC Purchase Order Table",
                row_name,
                "status",
                purchase_order.status
            )

def update_lc_purchase_order_status_from_receipt(doc, method):
    if not doc.custom_purchase_order:
        return

    purchase_order = frappe.get_doc("Purchase Order", doc.custom_purchase_order)

    if not purchase_order.custom_lc_number:
        return
    validate_lc_is_editable(purchase_order.custom_lc_number)

    row_name = frappe.db.get_value(
        "LC Purchase Order Table",
        {
            "parent": purchase_order.custom_lc_number,
            "purchase_order": purchase_order.name
        },
        "name"
    )

    if row_name:
        frappe.db.set_value(
            "LC Purchase Order Table",
            row_name,
            "status",
            purchase_order.status
        )


def update_lc_purchase_receipt_status_from_invoice(doc, method):
    for item in doc.items:
        if not item.purchase_receipt:
            continue

        purchase_receipt = frappe.get_doc("Purchase Receipt", item.purchase_receipt)

        if not purchase_receipt.custom_lc_number:
            continue
        validate_lc_is_editable(purchase_receipt.custom_lc_number)

        row_name = frappe.db.get_value(
            "LC Purchase Receipt Table",
            {
                "parent": purchase_receipt.custom_lc_number,
                "receipt_number": purchase_receipt.name
            },
            "name"
        )

        if row_name:
            frappe.db.set_value(
                "LC Purchase Receipt Table",
                row_name,
                "status",
                purchase_receipt.status
            )