import frappe

def execute():

    # Collapsible Capitalization Section
    if not frappe.db.exists("Custom Field", "Asset-capitalization_section"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Asset",
            "label": "Capitalization Info",
            "fieldtype": "Section Break",
            "fieldname": "capitalization_section",
            "insert_after": "other_details",
            "collapsible": 1,
        }).insert(ignore_permissions=True)

    # First custom field
    if not frappe.db.exists("Custom Field", "Asset-opening_accumulated"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Asset",
            "label": "Opening Accumulated Depreciation",
            "fieldtype": "Data",
            "fieldname": "opening_accumulated",
            "insert_after": "capitalization_section"
        }).insert(ignore_permissions=True)

    # Second custom field
    if not frappe.db.exists("Custom Field", "Asset-opening_number"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Asset",
            "label": "Opening Number of Booked Depreciations",
            "fieldtype": "Data",
            "fieldname": "opening_number",
            "insert_after": "opening_accumulated"
        }).insert(ignore_permissions=True)

    if not frappe.db.exists("Custom Field", "Asset-is_capitalized"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Asset",
            "label": "Is Capitalized",
            "fieldtype": "Check",
            "fieldname": "is_capitalized",
            "insert_after": "opening_number"
        }).insert(ignore_permissions=True)

    # 5️⃣ Child Table
    if not frappe.db.exists("Custom Field", "Asset-capitalization_details"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Asset",
            "label": "Capitalization Details",
            "fieldtype": "Table",
            "fieldname": "capitalization_details",
            "options": "Asset Capitalization Detail",
            "depends_on": "eval:doc.is_capitalized == 1",
            "insert_after": "is_capitalized"
        }).insert(ignore_permissions=True)

    # 6️⃣ Closing Section Break
    if not frappe.db.exists("Custom Field", "Asset-capitalization_section_end"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Asset",
            "label": "",
            "fieldtype": "Section Break",
            "fieldname": "capitalization_section_end",
            "insert_after": "capitalization_details"
        }).insert(ignore_permissions=True)

    frappe.clear_cache()
