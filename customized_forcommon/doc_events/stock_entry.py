import frappe


def validate_overreturn(doc, method=None):

    if doc.stock_entry_type != "Material Return":
        return

    if not doc.custom_return_against:
        frappe.throw("Return Against is required for Material Return")

    original = frappe.get_doc("Stock Entry", doc.custom_return_against)

    issued = {}
    returned = {}

    # issued qty
    for d in original.items:
        key = (d.item_code, d.s_warehouse)
        issued[key] = issued.get(key, 0) + d.qty

    # already returned qty
    existing_returns = frappe.get_all(
        "Stock Entry",
        filters={
            "custom_return_against": doc.custom_return_against,
            "docstatus": 1
        },
        pluck="name"
    )

    for se in existing_returns:
        se_doc = frappe.get_doc("Stock Entry", se)
        for d in se_doc.items:
            key = (d.item_code, d.t_warehouse)
            returned[key] = returned.get(key, 0) + d.qty

    # current return validation
    for d in doc.items:
        key = (d.item_code, d.t_warehouse)
        total = returned.get(key, 0) + d.qty
        if total > issued.get(key, 0):
            frappe.throw(
                    f"Over-return not allowed in Stock Entry {doc.name} for Item <b>{d.item_code}</b>"
                )