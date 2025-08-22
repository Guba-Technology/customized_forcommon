import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    purchase_invoice_meta = frappe.get_meta("Purchase Invoice")
    existing_fields = [df.fieldname for df in purchase_invoice_meta.fields]

    target_fields = {
        "custom_vat_details",
        "custom_vat_category",
        "custom_mrc_number",
        "custom_vat_details_col_1",
        "custom_type_of_purchase",
        "custom_vat_receipt_number",
        "custom_description"
    }

   
    if target_fields.intersection(existing_fields):
        return

    create_custom_fields({
        "Purchase Invoice": [
            dict(
                fieldname="custom_vat_details",
                label="VAT Details",
                fieldtype="Section Break",
                insert_after="total_advance",
                collapsible=1,
                module="custom report"
            ),
            dict(
                fieldname="custom_vat_category",
                label="VAT Category",
                fieldtype="Select",
                insert_after="custom_vat_details",
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
                fieldname="custom_vat_details_col_1",
                fieldtype="Column Break",
                insert_after="custom_vat_category",
                module="custom report"
            ),
            dict(
                fieldname="custom_type_of_purchase",
                label="Type of Purchase",
                fieldtype="Select",
                insert_after="custom_vat_details_col_1",
                options="\nTaxable-local Purchase of Capital Assets\nTaxable-imported Purchase of Capital Assets\nTaxable-local Purchase of Inputs\nTaxable-imported Purchase of Inputs\nTaxable-general Expense Inputs Purchase\nTax Exempted-purchase with no vat or uncollectible inputs",
                placeholder="Type of Purchase",
                module="custom report"
            ),
            dict(
                fieldname="custom_vat_receipt_number",
                label="VAT Receipt Number",
                fieldtype="Data",
                insert_after="custom_type_of_purchase",
                placeholder="VAT Receipt Number",
                module="custom report"
            ),
            dict(
                fieldname="custom_description",
                label="Description",
                fieldtype="Text Editor",
                insert_after="custom_vat_receipt_number",
                placeholder="write a purchase VAT description here",
                module="custom report"
            )
        ]
    })
