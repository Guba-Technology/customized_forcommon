import frappe

def land_cost_creation_checker_for_purchase_order(doc, method):
    for row in doc.purchase_receipts or []:

        if row.receipt_document_type != "Purchase Receipt":
            continue

        pr = frappe.get_doc("Purchase Receipt", row.receipt_document)

        if not pr.custom_purchase_order:
            continue

        po = frappe.get_doc("Purchase Order", pr.custom_purchase_order)

        if not po.custom_lc_number:
            continue

        if frappe.db.exists(
            "LC Purchase Order Table",
            {
                "parent": po.custom_lc_number,
                "purchase_order": po.name
            }
        ):
            frappe.db.set_value(
                "LC Master",
                po.custom_lc_number,
                "is_landed_cost_created",
                1
            )