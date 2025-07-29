import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    # Check if field already exists in meta (standard or custom)
    appraisal = frappe.get_meta("Appraisal")
    if "status" in [df.fieldname for df in appraisal.fields]:
        return

    # Otherwise, create the custom field
    create_custom_fields({
        "Appraisal": [
            dict(
                fieldname="status",
                label="Status",
                fieldtype="Select",
                options="Pending\nApproved\nCancelled",
                insert_after="appraisal_cycle",
                reqd=0
            )
        ]
    })
