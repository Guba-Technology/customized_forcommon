import frappe

changed = False
def upsert_custom_field(doctype, field_def):
    fieldname = field_def["fieldname"]
    field_id = f"{doctype}-{fieldname}"

    try:
        try:
            custom_field = frappe.get_doc("Custom Field", field_id)
            updated = False
            for key, value in field_def.items():
                if key != "fieldname" and custom_field.get(key) != value:
                    custom_field.set(key, value)
                    updated = True
                    global changed
                    changed = True

            if updated:
                custom_field.save()
                frappe.db.commit()
                #print(f"✍️ Updated: {field_id}")
            

        except frappe.DoesNotExistError:
            field_def["dt"] = doctype
            frappe.get_doc({
                "doctype": "Custom Field",
                **field_def
            }).insert()
            frappe.db.commit()
            changed = True
            #print(f"🆕 Created: {field_id}")
    except frappe.QueryTimeoutError:
        print(f"⏳ Skipped due to lock: {field_id}")
    except Exception as e:
        print(f"❌ Error: {field_id}: {e}")

def execute():
    doctype = "Sales Invoice"
    fields = [
        dict(fieldname="custom_withholding_detail", label="Withholding Detail", fieldtype="Section Break", insert_after="outstanding_amount", collapsible=1, module="custom report"),
        dict(fieldname="custom_withholding_detail_col_1", fieldtype="Column Break", insert_after="custom_withholding_detail", module="custom report"),
        dict(fieldname="custom_receipt_number", label="Receipt Number", fieldtype="Data", insert_after="custom_withholding_detail_col_1", placeholder="Receipt Number", module="custom report"),
        dict(fieldname="custom_withholding_detail_col_2", fieldtype="Column Break", insert_after="custom_receipt_number", module="custom report"),
        dict(fieldname="custom_withhold_date", label="Withhold Date", fieldtype="Date", insert_after="custom_withholding_detail_col_2", placeholder="Withhold Date", module="custom report"),
        dict(fieldname="custom_vat_details", label="VAT Details", fieldtype="Section Break", insert_after="custom_withhold_date", collapsible=1, module="custom report"),
        dict(fieldname="custom_vat_details_col_1", fieldtype="Column Break", insert_after="custom_vat_details", module="custom report"),
        dict(fieldname="custom_vat_category", label="VAT Category", fieldtype="Select", insert_after="custom_vat_details_col_1", options="\ngood\nservices", placeholder="VAT Category", module="custom report"),
        dict(fieldname="custom_mrc_number", label="MRC Number", fieldtype="Data", insert_after="custom_vat_category", placeholder="MRC Number", module="custom report"),
        dict(fieldname="custom_vat_date", label="VAT Date", fieldtype="Date", insert_after="custom_mrc_number", placeholder="VAT Date", module="custom report"),
        dict(fieldname="custom_vat_details_col_2", fieldtype="Column Break", insert_after="custom_vat_date", module="custom report"),
        dict(fieldname="custom_type_of_sale", label="Type of Sale", fieldtype="Select", insert_after="custom_vat_details_col_2", options="\ntaxable sale\nzero rated sale\nexempted sale", placeholder="Type of Sale", module="custom report"),
        dict(fieldname="custom_vat_receipt_number", label="VAT Receipt Number", fieldtype="Data", insert_after="custom_type_of_sale", placeholder="VAT Receipt Number", module="custom report"),
        dict(fieldname="custom_description", label="Descriptions", fieldtype="Text Editor", insert_after="custom_vat_receipt_number", placeholder="write the VAT Description here", module="custom report")
    ]
    
    for field in fields:
        frappe.db.autocommit = False
        upsert_custom_field(doctype, field)
        frappe.db.autocommit = True
 
    #print("✅ Sales Invoice Patch completed successfully.")

    if changed:
        print("✅ Sales Invoice Patch completed successfully.")
   