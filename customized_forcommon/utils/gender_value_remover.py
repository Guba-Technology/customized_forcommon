# customized_forcommon/patches/v1/gender_patch.py
import frappe

def execute(*args, **kwargs):
    """
    Ensures only default genders exist: Male and Female.
    Deletes any other Gender records.
    """
    default_genders = ["Male", "Female"]

    # Delete any Gender that is not in default_genders
    frappe.db.delete(
        "Gender",
        filters=[["gender", "not in", default_genders]]
    )

    # Insert missing default genders if they do not exist
    for gender in default_genders:
        if not frappe.db.exists("Gender", {"gender": gender}):
            frappe.get_doc({
                "doctype": "Gender",
                "gender": gender
            }).insert(ignore_permissions=True)

    frappe.db.commit()