import frappe

def update_lc_master_totals(doc, method):

    processed_lcs = set()

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

        if not lc_number or lc_number in processed_lcs:
            continue

        processed_lcs.add(lc_number)

        lc_master = frappe.get_doc(
            "LC Master",
            lc_number
        )


        # CIF configured accounts in LC Master
        cif_accounts = {
            account_row.cif_value_account
            for account_row in lc_master.cif_value_accounts
        }


        cif_total = 0
        overhead_total = 0


        # Calculate from Landed Cost Voucher taxes
        for tax_row in doc.taxes:

            amount = tax_row.amount or 0

            if tax_row.expense_account in cif_accounts:
                cif_total += amount
            else:
                overhead_total += amount


        total_cost = (
            (lc_master.total_fob_amount or 0)
            + cif_total
            + overhead_total
        )


        frappe.db.set_value(
            "LC Master",
            lc_number,
            {
                "cif_value": cif_total,
                "total_overhead_cost": overhead_total,
                "total_cost": total_cost,
            }
        )

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
                "created_landed_cost_voucher": doc.name,
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
                "status": "Open",
                "created_landed_cost_voucher": None
            }
        )
