import frappe

def execute():
    """
    Patch Employee naming rule to empty list
    """
    # Fetch the Employee doctype
    doctype = "Employee"

    # Clear naming rules
    if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": "naming_series"}):
        # Optional: if a custom field exists
        frappe.delete_doc("Custom Field", frappe.db.get_value("Custom Field", {"dt": doctype, "fieldname": "naming_series"}))
    
    # Clear naming rules from DocType settings
    frappe.db.set_value("DocType", doctype, "autoname", "prompt")  # 'prompt' disables automatic series
    frappe.db.commit()
    print(f"{doctype} autoname and naming rules patched to empty.")
