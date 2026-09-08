import frappe

def execute():
    field_name = "payment_request_type"
    doctype_name = "Payment Request"

    # Fetch field metadata
    field = frappe.get_doc("DocField", {"parent": doctype_name, "fieldname": field_name})
    if not field:
        frappe.log_error("Payment Request Type field not found")
        return

    # Existing options
    options = field.options.split("\n") if field.options else []

    # Add if missing
    if "Internal Transfer" not in options:
        options.append("Internal Transfer")
        field.options = "\n".join(options)
        field.save()
        frappe.db.commit()
        frappe.clear_cache(doctype=doctype_name)
        frappe.logger().info("✔ Internal Transfer added to Payment Request Type")
    else:
        frappe.logger().info("ℹ Internal Transfer already exists")
