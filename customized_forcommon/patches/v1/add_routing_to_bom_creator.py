import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    # Check if field already exists in meta (standard or custom)
    bomcreator = frappe.get_meta("Bom Creator")
    if "routing" in [df.fieldname for df in bomcreator.fields]:
        return

    # Otherwise, create the custom field
    create_custom_fields({
        "Bom Creator": [
            dict(
                fieldname="section_break_xvld",
                label="Operations Routing",
                fieldtype="Section Break",
                insert_after="error_log"
            ),
            dict(
                fieldname="routing",
                label="Routing",
                fieldtype="Link",
                options="Routing",
                insert_after="section_break_xvld"
            )
        ]
    })
