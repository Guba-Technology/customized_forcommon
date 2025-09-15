import frappe
from frappe.exceptions import QueryTimeoutError, DoesNotExistError
 
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

            if updated:
                custom_field.save()
                frappe.db.commit()
                print(f"✍️ Updated: {field_id}")
            

        except DoesNotExistError:
            field_def["dt"] = doctype
            frappe.get_doc({
                "doctype": "Custom Field",
                **field_def
            }).insert()
            frappe.db.commit()
            #print(f"🆕 Created: {field_id}")
    except QueryTimeoutError:
        print(f"⏳ Skipped due to lock: {field_id}")
    except Exception as e:
        print(f"❌ Error on {field_id}: {e}") 

def execute():
    doctype = "Company"
    fields = [
        dict(fieldname="custom_vat_account", label="VAT Account", fieldtype="Tab Break", insert_after="dashboard_tab", module="custom report"),
        dict(fieldname="custom_vat_account_information", label="VAT Account Information", fieldtype="Section Break", insert_after="custom_vat_account", module="custom report"),
        dict(fieldname="custom_vat_account_col_1", fieldtype="Column Break", insert_after="custom_vat_account_information", module="custom report"),
        dict(fieldname="custom_vat_payable_account", label="VAT Payable Account", fieldtype="Link", options="Account", insert_after="custom_vat_account_col_1", placeholder="VAT Payable Account", module="custom report"),
        dict(fieldname="custom_withholding_payable_account", label="Withholding Payable Account", fieldtype="Link", options="Account", insert_after="custom_vat_payable_account", placeholder="Withholding Payable Account", module="custom report"),
        dict(fieldname="custom_pension_payable_account", label="Pension Payable Account", fieldtype="Link", options="Account", insert_after="custom_withholding_payable_account", placeholder="Pension Payable Account", module="custom report"),
        dict(fieldname="custom_vat_account_col_2", fieldtype="Column Break", insert_after="custom_pension_payable_account", module="custom report"),
        dict(fieldname="custom_vat_receivable_account", label="VAT Receivable Account", fieldtype="Link", options="Account", insert_after="custom_vat_account_col_2", placeholder="VAT Receivable Account", module="custom report"),
        dict(fieldname="custom_withholding_receivable_account", label="Withholding Receivable Account", fieldtype="Link", options="Account", insert_after="custom_vat_receivable_account", placeholder="Withholding Receivable Account", module="custom report"),
        dict(fieldname="custom_pension_receivable_account", label="Pension Receivable Account", fieldtype="Link", options="Account", insert_after="custom_withholding_receivable_account", placeholder="Pension Receivable Account", module="custom report")
    ]

    for field in fields:
        frappe.db.autocommit = False
        upsert_custom_field(doctype, field)
        frappe.db.autocommit = True
    print("✅ Company Patch completed successfully.")