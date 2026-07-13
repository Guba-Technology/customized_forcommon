import frappe

def execute():
    """Patch to ensure 'Cane Receipt' is included in Material Request.purpose options."""
    field = frappe.db.get_value(
        "DocField",
        {"parent": "Material Request", "fieldname": "purpose"},
        ["name", "options"],
        as_dict=True,
    )

    if not field:
        frappe.log_error("Material Request field 'purpose' not found.")
        return

    options = field.options.split("\n") if field.options else []
    updated = False

    for opt in ["Cane Receipt"]:
        if opt not in options:
            options.append(opt)
            updated = True

    if updated:
        frappe.db.set_value("DocField", field.name, "options", "\n".join(options))
        frappe.clear_cache(doctype="Material Request")
