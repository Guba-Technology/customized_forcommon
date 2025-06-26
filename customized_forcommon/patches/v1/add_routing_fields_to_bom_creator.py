from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    create_custom_fields({
        "BOM Creator": [
            {
                "fieldname": "section_break_xvld",
                "label": "Operations Routing",
                "fieldtype": "Section Break",
                "insert_after": "uom"
            },
            {
                "fieldname": "routing",
                "label": "Routing",
                "fieldtype": "Link",
                "options": "Routing",
                "insert_after": "section_break_xvld"
            }
        ]
    })
