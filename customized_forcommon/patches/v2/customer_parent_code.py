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
    

    doctype = "Customer"
    fields = [
        dict(fieldname="parent_code", label="Parent Code", fieldtype="Data", insert_after="customer_group", placeholder="Parent Code", module="custom report")
    ]

    for field in fields:
        upsert_custom_field(doctype, field)
 
    print("✅ Customer Patch completed successfully.")
