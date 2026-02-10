import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    # Check if field already exists in meta (standard or custom)
    user = frappe.get_meta("User")
    if "company" in [df.fieldname for df in user.fields]:
        return

    # Otherwise, create the custom field
    create_custom_fields({
        "User": [
            dict(
                fieldname="company",
                label="Company",
                fieldtype="Link",
                options="Company",
                insert_after="username",
                reqd=1
            )
        ]
    })
