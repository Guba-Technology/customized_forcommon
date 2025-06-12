import frappe

def execute():
    # Step 1: Enable in_create on the Gender DocType
    doc = frappe.get_doc("DocType", "Gender")
    doc.in_create = 1
    doc.save()

    # Step 2: Delete all existing Gender records
    frappe.db.delete("Gender")

    # Step 3: Insert default gender values
    gender_list = ["Male", "Female"]
    for g in gender_list:
        gender_doc = frappe.get_doc({
            "doctype": "Gender",
            "gender": g  # Ensure this matches your field name in the Gender DocType
        })
        gender_doc.insert(ignore_permissions=True)

    frappe.db.commit()