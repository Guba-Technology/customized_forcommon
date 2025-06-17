import frappe

def execute():
    doctype = "Employee Group Table"
    old_label = "ERPNext User ID"
    new_label = "ERP User ID"

    # Get the fieldname of the existing field by label
    field = frappe.db.get_value(
        "DocField",
        {"parent": doctype, "label": old_label},
        ["name", "fieldname"]
    )

    if field:
        fieldname = field[1]

        # Rename the label
        frappe.db.set_value(
            "DocField",
            {"parent": doctype, "fieldname": fieldname},
            "label",
            new_label
        )

        frappe.clear_cache(doctype=doctype)

        frappe.logger().info(
            f"Renamed label of field '{fieldname}' in {doctype} from '{old_label}' to '{new_label}'"
        )
    else:
        frappe.logger().warn(f"No field with label '{old_label}' found in {doctype}")

    # Commit the transaction to ensure changes persist
    frappe.db.commit()
