# customized_forcommon/patches/v1/change_label.py
import frappe

def execute():
    # Check if Property Setter already exists
    if not frappe.db.exists("Property Setter", {
        "doc_type": "Employee",
        "field_name": "salutation",
        "property": "label"
    }):
        ps = frappe.get_doc({
            "doctype": "Property Setter",
            "doctype_or_field": "DocField",   
            "doc_type": "Employee",
            "field_name": "salutation",
            "property": "label",
            "property_type": "Data",
            "value": "Title"
        })
        ps.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Property Setter created: Salutation → Title")
    else:
        print("Property Setter already exists")

    # --- Hide portal_users_tab ---
    if not frappe.db.exists("Property Setter", {
        "doc_type": "Customer",
        "field_name": "portal_users_tab",
        "property": "hidden"
    }):
        ps_tab = frappe.get_doc({
            "doctype": "Property Setter",
            "doctype_or_field": "DocField",
            "doc_type": "Customer",
            "field_name": "portal_users_tab",
            "property": "hidden",
            "property_type": "Check",
            "value": 1
        })
        ps_tab.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Property Setter created: portal_users_tab → Hidden")
    else:
        print("Property Setter for portal_users_tab already exists")