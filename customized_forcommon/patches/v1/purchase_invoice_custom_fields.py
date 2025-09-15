import frappe

def upsert_custom_field(doctype, field_def):
    fieldname = field_def["fieldname"]
    field_id = f"{doctype}-{fieldname}"

    try:
        custom_field = frappe.get_doc("Custom Field", field_id)
        updated = False
        for key, value in field_def.items():
            if key != "fieldname" and custom_field.get(key) != value:
                custom_field.set(key, value)
                updated = True

        if updated:
            custom_field.save()
            frappe.db.commit()
            print(f"✍️ Updated: {field_id}")


    except frappe.DoesNotExistError:
        field_def["dt"] = doctype
        frappe.get_doc({
            "doctype": "Custom Field",
            **field_def
        }).insert()
        frappe.db.commit()
        #print(f"🆕 Created: {field_id}")

def execute():
  
    doctype = "Purchase Invoice"
    fields = [
        dict(fieldname="custom_withholding_detail", label="Withholding Detail", fieldtype="Section Break", insert_after="outstanding_amount", collapsible=1, module="custom report"),
        dict(fieldname="custom_withholding_detail_col_1", fieldtype="Column Break", insert_after="custom_withholding_detail", module="custom report"),
        dict(fieldname="custom_receipt_number", label="Receipt Number", fieldtype="Data", insert_after="custom_withholding_detail_col_1", placeholder="Receipt Number", module="custom report"),
        dict(fieldname="custom_withholding_detail_col_2", fieldtype="Column Break", insert_after="custom_receipt_number", module="custom report"),
        dict(fieldname="custom_withhold_date", label="Withhold Date", fieldtype="Date", insert_after="custom_withholding_detail_col_2", placeholder="Withhold Date", module="custom report"),
        dict(fieldname="custom_vat_details", label="VAT Details", fieldtype="Section Break", insert_after="custom_withhold_date", collapsible=1, module="custom report"),
        dict(fieldname="custom_vat_category", label="VAT Category", fieldtype="Select", insert_after="custom_vat_details", options="\ngood\nservices", placeholder="VAT Category", module="custom report"),
        dict(fieldname="custom_mrc_number", label="MRC Number", fieldtype="Data", insert_after="custom_vat_category", placeholder="MRC Number", module="custom report"),
        dict(fieldname="custom_vat_date", label="VAT Date", fieldtype="Date", insert_after="custom_mrc_number", placeholder="VAT Date", module="custom report"),
        dict(fieldname="custom_vat_details_col_1", fieldtype="Column Break", insert_after="custom_vat_date", module="custom report"),
        dict(fieldname="custom_type_of_purchase", label="Type of Purchase", fieldtype="Select", insert_after="custom_vat_details_col_1", options="\nTaxable-local Purchase of Capital Assets\nTaxable-imported Purchase of Capital Assets\nTaxable-local Purchase of Inputs\nTaxable-imported Purchase of Inputs\nTaxable-general Expense Inputs Purchase\nTax Exempted-purchase with no vat or uncollectible inputs", placeholder="Type of Purchase", module="custom report"),
        dict(fieldname="custom_vat_receipt_number", label="VAT Receipt Number", fieldtype="Data", insert_after="custom_type_of_purchase", placeholder="VAT Receipt Number", module="custom report"),
        dict(fieldname="custom_description", label="Description", fieldtype="Text Editor", insert_after="custom_vat_receipt_number", placeholder="write a purchase VAT description here", module="custom report")
    ]

    for field in fields:
        upsert_custom_field(doctype, field)
    print("✅ Purchase Invoice Patch completed successfully.")