import frappe

def execute():
    """Patch to ensure 'Foreign' and 'Local' are included in Customer.customer_type options."""
    field = frappe.db.get_value(
        "DocField",
        {"parent": "Customer", "fieldname": "customer_type"},
        ["name", "options"],
        as_dict=True,
    )

    if not field:
        frappe.log_error("Customer field 'customer_type' not found.")
        return

    options = field.options.split("\n") if field.options else []
    updated = False

    for opt in ["Foreign", "Local"]:
        if opt not in options:
            options.append(opt)
            updated = True

    if updated:
        frappe.db.set_value("DocField", field.name, "options", "\n".join(options))
        frappe.clear_cache(doctype="Customer")
