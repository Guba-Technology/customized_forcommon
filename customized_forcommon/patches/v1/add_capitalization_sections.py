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
            "fieldtype": "Float",
            "fieldname": "opening_accumulated",
            "insert_after": "capitalization_section"
        }).insert(ignore_permissions=True)

    # Second custom field
    if not frappe.db.exists("Custom Field", "Asset-opening_number"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Asset",
            "label": "Opening Number of Booked Depreciations",
            "fieldtype": "Float",
            "fieldname": "opening_number",
            "insert_after": "opening_accumulated"
        }).insert(ignore_permissions=True)
    # NEW: Column Break after opening_accumulated
    if not frappe.db.exists("Custom Field", "Asset-column_break_opening"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Asset",
            "label": "",
            "fieldtype": "Column Break",
            "fieldname": "column_break_opening",
            "insert_after": "opening_number"
        }).insert(ignore_permissions=True)

    # NEW: First Purchase Amount field
    if not frappe.db.exists("Custom Field", "Asset-first_purchase_amount"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Asset",
            "label": "First Purchase Amount",
            "fieldtype": "Currency",
            "fieldname": "first_purchase_amount",
            "insert_after": "column_break_opening"
        }).insert(ignore_permissions=True)

    if not frappe.db.exists("Custom Field", "Asset-capitalization_full_width"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Asset",
            "label": "",
            "fieldtype": "Section Break",
            "fieldname": "capitalization_full_width",
            "insert_after": "first_purchase_amount"
        }).insert(ignore_permissions=True)

    if not frappe.db.exists("Custom Field", "Asset-is_capitalized"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Asset",
            "label": "Is Capitalized",
            "fieldtype": "Check",
            "fieldname": "is_capitalized",
            "default": "1",
            "insert_after": "capitalization_full_width"
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
            "depends_on": "eval:doc.is_capitalized == 1 || doc.docstatus == 1",
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