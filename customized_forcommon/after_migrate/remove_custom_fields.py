import frappe


def delete_custom_fields():
    custom_fields = [
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

    for fieldname in custom_fields:
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

    frappe.db.commit()