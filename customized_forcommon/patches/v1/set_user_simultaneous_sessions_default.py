import frappe

def execute():
    # Set default value of 'simultaneous_sessions' in User doctype to 1
    property_name = "default"
    doctype = "User"
    fieldname = "simultaneous_sessions"

    # Check if a Property Setter already exists
    existing = frappe.db.exists(
        "Property Setter",
        {
            "doctype_or_field": "DocField",
            "doc_type": doctype,
            "field_name": fieldname,
            "property": property_name
        }
    )

    if existing:
        # Update existing Property Setter
        ps = frappe.get_doc("Property Setter", existing)
        ps.value = "1"
        ps.save()
        frappe.db.commit()
        print(f"Updated Property Setter for {doctype}.{fieldname}")
    else:
        # Create new Property Setter
        ps = frappe.get_doc({
            "doctype": "Property Setter",
            "doctype_or_field": "DocField",
            "doc_type": doctype,
            "field_name": fieldname,
            "property": property_name,
            "property_type": "Small Text",
            "value": "1",
        })
        ps.insert()
        frappe.db.commit()
        print(f"Created Property Setter for {doctype}.{fieldname}")