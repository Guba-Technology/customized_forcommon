import frappe
from frappe.exceptions import QueryTimeoutError, DoesNotExistError

import frappe



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
                custom_field.save(ignore_permissions=True)
                frappe.db.commit()
                print(f"✍️ Updated: {field_id}")
            # else:
            #     print(f"✅ No changes needed: {field_id}")

        except DoesNotExistError:
            field_def["dt"] = doctype
            frappe.get_doc({
                "doctype": "Custom Field",
                **field_def
            }).insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"🆕 Created: {field_id}")

    except QueryTimeoutError:
        
        print(f"⏳ Skipped due to lock: {field_id}")
    except Exception as e:
        print(f"❌ Error on {field_id}: {e}")

def execute():
    doctype = "Employee"
    fields = [
        dict(fieldname="custom_additionals", label="Additional Details", fieldtype="Section Break", insert_after="custom_step", collapsible=1, module="custom report"),
        dict(fieldname="custom_additional_col1", fieldtype="Column Break", insert_after="custom_additionals", module="custom report"),
        dict(fieldname="pension_id", label="PID", fieldtype="Data", insert_after="custom_additional_col1", placeholder="Employee Pension ID", module="custom report"),
        dict(fieldname="custom_additional_col2", fieldtype="Column Break", insert_after="pension_id", module="custom report"),
        dict(fieldname="tin_number", label="Employee TIN", fieldtype="Data", insert_after="custom_additional_col2", placeholder="Employee TIN", module="custom report")
    ]

    for field in fields:
        frappe.db.autocommit = False
        upsert_custom_field(doctype, field)
        frappe.db.autocommit = True

    print("✅ Employee Patch completed successfully.")

    frappe.db.commit()