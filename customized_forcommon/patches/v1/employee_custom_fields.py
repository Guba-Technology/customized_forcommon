import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    employee_meta = frappe.get_meta("Employee")
    existing_fields = [df.fieldname for df in employee_meta.fields]

    target_fields = {
        "custom_additionals",
        "custom_additional_col1",
        "custom_pid",
        "custom_additional_col2",
        "custom_employee_tin"
    }

    if target_fields.intersection(existing_fields):
        return

    create_custom_fields({
        "Employee": [
            dict(
                fieldname="custom_additionals",
                label="Additionals",
                fieldtype="Section Break",
                insert_after="custom_step",
                collapsible=1,
                module="custom report"
            ),
            dict(
                fieldname="custom_additional_col1",
                fieldtype="Column Break",
                insert_after="custom_additionals",
                module="custom report"
            ),
            dict(
                fieldname="custom_pid",
                label="PID",
                fieldtype="Data",
                insert_after="custom_additional_col1",
                placeholder="Employee Pension ID",
                module="custom report"
            ),
            dict(
                fieldname="custom_additional_col2",
                fieldtype="Column Break",
                insert_after="custom_pid",
                module="custom report"
            ),
            dict(
                fieldname="tin_number",
                label="Employee TIN",
                fieldtype="Data",
                insert_after="custom_additional_col2",
                placeholder="Employee TIN",
                module="custom report"
            )
        ]
    })
