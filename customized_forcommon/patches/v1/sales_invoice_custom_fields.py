import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    sales_invoice_meta = frappe.get_meta("Sales Invoice")
    existing_fields = [df.fieldname for df in sales_invoice_meta.fields]

    target_fields = {
        "custom_withholding_detail",
        "custom_withholding_detail_col_1",
        "custom_receipt_number",
        "custom_withholding_detail_col_2",
        "custom_withhold_date",
        "custom_vat_details",
        "custom_vat_details_col_1",
        "custom_vat_category",
        "custom_mrc_number",
        "custom_vat_details_col_2",
        "custom_type_of_sale",
        "custom_vat_receipt_number",
        "custom_description"
    }

    if target_fields.intersection(existing_fields):
        return

    create_custom_fields({
        "Sales Invoice": [
            dict(
                fieldname="custom_withholding_detail",
                label="Withholding Detail",
                fieldtype="Section Break",
                insert_after="outstanding_amount",
                collapsible=1,
                module="custom report"
            ),
            dict(
                fieldname="custom_withholding_detail_col_1",
                fieldtype="Column Break",
                insert_after="custom_withholding_detail",
                module="custom report"
            ),
            dict(
                fieldname="custom_receipt_number",
                label="Receipt Number",
                fieldtype="Data",
                insert_after="custom_withholding_detail_col_1",
                placeholder="Receipt Number",
                module="custom report"
            ),
            dict(
                fieldname="custom_withholding_detail_col_2",
                fieldtype="Column Break",
                insert_after="custom_receipt_number",
                module="custom report"
            ),
            dict(
                fieldname="custom_withhold_date",
                label="Withhold Date",
                fieldtype="Date",
                insert_after="custom_withholding_detail_col_2",
                placeholder="Withhold Date",
                module="custom report"
            ),
            dict(
                fieldname="custom_vat_details",
                label="VAT Details",
                fieldtype="Section Break",
                insert_after="custom_withhold_date",
                collapsible=1,
                module="custom report"
            ),
            dict(
                fieldname="custom_vat_details_col_1",
                fieldtype="Column Break",
                insert_after="custom_vat_details",
                module="custom report"
            ),
            dict(
                fieldname="custom_vat_category",
                label="VAT Category",
                fieldtype="Select",
                insert_after="custom_vat_details_col_1",
                options="\ngood\nservices",
                placeholder="VAT Category",
                module="custom report"
            ),
            dict(
                fieldname="custom_mrc_number",
                label="MRC Number",
                fieldtype="Data",
                insert_after="custom_vat_category",
                placeholder="MRC Number",
                module="custom report"
            ),
            dict(
                fieldname="custom_vat_details_col_2",
                fieldtype="Column Break",
                insert_after="custom_vat_category",
                module="custom report"
            ),
            dict(
                fieldname="custom_type_of_sale",
                label="Type of Sale",
                fieldtype="Select",
                insert_after="custom_vat_details_col_2",
                options="\ntaxable sale\nzero rated sale\nexempted sale",
                placeholder="Type of Sale",
                module="custom report"
            ),
            dict(
                fieldname="custom_vat_receipt_number",
                label="VAT Receipt Number",
                fieldtype="Data",
                insert_after="custom_type_of_sale",
                placeholder="VAT Receipt Number",
                module="custom report"
            ),
            dict(
                fieldname="custom_description",
                label="Description",
                fieldtype="Text Editor",
                insert_after="custom_vat_receipt_number",
                placeholder="write the VAT Description here",
                module="custom report"
            )
        ]
    })
