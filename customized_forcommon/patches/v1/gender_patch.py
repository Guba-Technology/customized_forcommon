import frappe

def execute():
    # Step 1: Delete all existing Gender records
    frappe.db.delete("Gender")

    # Step 2: Insert default gender values
    gender_list = ["Male", "Female"]
    for gender in gender_list:
        gender_doc = frappe.get_doc({
            "doctype": "Gender",
            "gender": gender,  # Ensure this matches your field name in the Gender DocType
        })
        gender_doc.insert(ignore_permissions=True)

    frappe.db.commit()