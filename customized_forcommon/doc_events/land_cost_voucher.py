import frappe


def land_cost_creation_checker_for_purchase_order(doc, method):

    lc_numbers = set()

    for row in doc.purchase_receipts or []:

        if row.receipt_document_type != "Purchase Receipt":
            continue

        po_name = frappe.db.get_value(
            "Purchase Receipt",
            row.receipt_document,
            "custom_purchase_order"
        )

        if not po_name:
            continue

        lc_number = frappe.db.get_value(
            "Purchase Order",
            po_name,
            "custom_lc_number"
        )

        if not lc_number:
            continue

        if frappe.db.exists(
            "LC Purchase Order Table",
            {
                "parent": lc_number,
                "purchase_order": po_name
            }
        ):
            lc_numbers.add(lc_number)


    for lc in lc_numbers:
        frappe.db.set_value(
            "LC Master",
            lc,
            {
                "is_landed_cost_created": 1,
                "status": "Closed"
            },
        )

def reopen_lc_after_land_cost_cancel(doc, method):

    lc_numbers = set()

    for row in doc.purchase_receipts or []:

        if row.receipt_document_type != "Purchase Receipt":
            continue

        po_name = frappe.db.get_value(
            "Purchase Receipt",
            row.receipt_document,
            "custom_purchase_order"
        )

        if not po_name:
            continue

        lc_number = frappe.db.get_value(
            "Purchase Order",
            po_name,
            "custom_lc_number"
        )

        if lc_number:
            lc_numbers.add(lc_number)


    for lc in lc_numbers:
        frappe.db.set_value(
            "LC Master",
            lc,
            {
                "is_landed_cost_created": 0,
                "status": "Open"
            }
        )