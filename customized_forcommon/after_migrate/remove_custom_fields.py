import frappe


def delete_custom_fields():
    material_request_custom_fields = [
        "custom_project_details",
        "custom_show_project_details",
        "custom_consultant",
        "custom_location",
        "custom_project_col2",
        "custom_contractor",
        "custom_task",
        "custom_project",
        "custom_project_col",
    ]

    company_custom_fields = [
        "custom_contractor_advance",
        "custom_contractor_payable",
        "custom_real_esate_project",
        "custom_project_col2",
        "custom_project_col1",
    ]

    # Delete Material Request custom fields
    for fieldname in material_request_custom_fields:
        custom_field = frappe.db.exists(
            "Custom Field",
            {
                "dt": "Material Request",
                "fieldname": fieldname,
            },
        )

        if not custom_field:
            continue

        frappe.delete_doc(
            "Custom Field",
            custom_field,
            force=True,
        )

        frappe.logger("migration").info(
            f"Deleted Custom Field {custom_field} from Material Request"
        )

    # Delete Company custom fields
    for fieldname in company_custom_fields:
        custom_field = frappe.db.exists(
            "Custom Field",
            {
                "dt": "Company",
                "fieldname": fieldname,
            },
        )

        if not custom_field:
            continue

        frappe.delete_doc(
            "Custom Field",
            custom_field,
            force=True,
        )

        frappe.logger("migration").info(
            f"Deleted Custom Field {custom_field} from Company"
        )

    frappe.db.commit()