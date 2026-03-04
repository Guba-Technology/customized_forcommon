import frappe
from frappe.exceptions import QueryTimeoutError, DoesNotExistError

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
            

        except DoesNotExistError:
            field_def["dt"] = doctype
            frappe.get_doc({
                "doctype": "Custom Field",
                **field_def
            }).insert()
            frappe.db.commit()
            changed = True
            #print(f"🆕 Created: {field_id}")
    except QueryTimeoutError:
        print(f"⏳ Skipped due to lock: {field_id}")
    except Exception as e:
        print(f"❌ Error on {field_id}: {e}") 

def execute():
    doctype = "Company"
    module = "custom report"

    fields = [
        dict(fieldname="custom_vat_account", label="VAT Account", fieldtype="Tab Break", insert_after="dashboard_tab", module=module),
        dict(fieldname="custom_vat_account_information", label="VAT Account Information", fieldtype="Section Break", insert_after="custom_vat_account", module=module),
        dict(fieldname="custom_vat_account_col_1", fieldtype="Column Break", insert_after="custom_vat_account_information", module=module),
        dict(fieldname="custom_vat_payable_account", label="VAT Payable Account", fieldtype="Link", options="Account", insert_after="custom_vat_account_col_1", placeholder="VAT Payable Account", module=module),
        dict(fieldname="custom_withholding_payable_account", label="Withholding Payable Account", fieldtype="Link", options="Account", insert_after="custom_vat_payable_account", placeholder="Withholding Payable Account", module=module),
        dict(fieldname="custom_vat_openning_amount", label="VAT Openning Amount", fieldtype="Currency", insert_after="custom_withholding_payable_account", placeholder="vat openning account", module=module),
        dict(fieldname="custom_vat_account_col_2", fieldtype="Column Break", insert_after="custom_vat_openning_amount", module=module),
        dict(fieldname="custom_vat_receivable_account", label="VAT Receivable Account", fieldtype="Link", options="Account", insert_after="custom_vat_account_col_2", placeholder="VAT Receivable Account", module=module),
        dict(fieldname="custom_withholding_receivable_account", label="Withholding Receivable Account", fieldtype="Link", options="Account", insert_after="custom_vat_receivable_account", placeholder="Withholding Receivable Account", module=module),
        dict(fieldname="vat_closings", label="VAT Closing", fieldtype="Table", insert_after="custom_withholding_receivable_account", options="VAT Closing", module=module, read_only=1)
    ]

   
    for field in fields:
        frappe.db.autocommit = False
        upsert_custom_field(doctype, field)
        frappe.db.autocommit = True

    
    existing_fields = frappe.get_all(
        "Custom Field",
        filters={"dt": doctype, "module": module},
        fields=["name", "fieldname"]
    )

    valid_fieldnames = {f["fieldname"] for f in fields}

    for field in existing_fields:
        if field["fieldname"] not in valid_fieldnames:
            try:
                try:
                    frappe.delete_doc("Custom Field", field["name"])
                    frappe.db.commit()
                    global changed
                    changed = True
                except Exception as e:
                    print(f"❌ Failed to remove {field['fieldname']}: {e}")
            except QueryTimeoutError as e:
                print(f"❌ Failed to remove {field['fieldname']}: {e}")
            except Exception as e:
                print(f"❌ Failed to remove {field['fieldname']}: {e}")

    # if changed:
    #     print("✅ Company is modified.")
