import frappe

def execute():
    """Force create Property Setters and update existing System Settings checkboxes"""

    property_setters = [
        # readonly
        {
            "doctype_or_field": "DocField",
            "doc_type": "System Settings",
            "field_name": "disable_system_update_notification",
            "property": "read_only",
            "value": 1,
            "property_type": "Check"
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "System Settings",
            "field_name": "disable_change_log_notification",
            "property": "read_only",
            "value": 1,
            "property_type": "Check"
        },
        # default for future records
        {
            "doctype_or_field": "DocField",
            "doc_type": "System Settings",
            "field_name": "disable_system_update_notification",
            "property": "default",
            "value": "1",
            "property_type": "Data"
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "System Settings",
            "field_name": "disable_change_log_notification",
            "property": "default",
            "value": "1",
            "property_type": "Data"
        }
    ]

    # Step 1: Create Property Setters
    for ps in property_setters:
        frappe.get_doc({
            "doctype": "Property Setter",
            "doctype_or_field": ps["doctype_or_field"],
            "doc_type": ps["doc_type"],
            "field_name": ps["field_name"],
            "property": ps["property"],
            "property_type": ps["property_type"],
            "value": ps["value"]
        }).insert(ignore_permissions=True, ignore_if_duplicate=True)

    # Step 2: Update the existing System Settings values directly in DB
    frappe.db.set_value("System Settings", None, "disable_system_update_notification", 1)
    frappe.db.set_value("System Settings", None, "disable_change_log_notification", 1)

    frappe.db.commit()