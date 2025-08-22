import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    company_meta = frappe.get_meta("Company")
    existing_fields = [df.fieldname for df in company_meta.fields]

    target_fields = {
        "custom_vat_account",
        "custom_vat_account_information",
        "custom_vat_account_col_1",
        "custom_vat_payable_account",
        "custom_withholding_payable_account",
        "custom_pension_payable_account",
        "custom_vat_account_col_2",
        "custom_vat_receivable_account",
        "custom_withholding_receivable_account",
        "custom_pension_receivable_account"
    }

    
    if target_fields.intersection(existing_fields):
        return

    create_custom_fields({
        "Company": [
            dict(
                fieldname="custom_vat_account",
                label="VAT Account",
                fieldtype="Tab Break",
                insert_after="dashboard_tab",
                module="custom report"
            ),
            dict(
                fieldname="custom_vat_account_information",
                label="VAT Account Information",
                fieldtype="Section Break",
                insert_after="custom_vat_account",
                module="custom report"
            ),
            dict(
                fieldname="custom_vat_account_col_1",
                fieldtype="Column Break",
                insert_after="custom_vat_account_information",
                module="custom report"
            ),
            dict(
                fieldname="custom_vat_payable_account",
                label="VAT Payable Account",
                fieldtype="Link",
                options="Account",
                insert_after="custom_vat_account_col_1",
                placeholder="VAT Payable Account",
                module="custom report"
            ),
            dict(
                fieldname="custom_withholding_payable_account",
                label="Withholding Payable Account",
                fieldtype="Link",
                options="Account",
                insert_after="custom_vat_payable_account",
                placeholder="Withholding Payable Account",
                module="custom report"
            ),
            dict(
                fieldname="custom_pension_payable_account",
                label="Pension Payable Account",
                fieldtype="Link",
                options="Account",
                insert_after="custom_withholding_payable_account",
                placeholder="Pension Payable Account",
                module="custom report"
            ),
            dict(
                fieldname="custom_vat_account_col_2",
                fieldtype="Column Break",
                insert_after="custom_pension_payable_account",
                module="custom report"
            ),
            dict(
                fieldname="custom_vat_receivable_account",
                label="VAT Receivable Account",
                fieldtype="Link",
                options="Account",
                insert_after="custom_vat_account_col_2",
                placeholder="VAT Receivable Account",
                module="custom report"
            ),
            dict(
                fieldname="custom_withholding_receivable_account",
                label="Withholding Receivable Account",
                fieldtype="Link",
                options="Account",
                insert_after="custom_vat_receivable_account",
                placeholder="Withholding Receivable Account",
                module="custom report"
            ),
            dict(
                fieldname="custom_pension_receivable_account",
                label="Pension Receivable Account",
                fieldtype="Link",
                options="Account",
                insert_after="custom_withholding_receivable_account",
                placeholder="Pension Receivable Account",
                module="custom report"
            )
        ]
    })
