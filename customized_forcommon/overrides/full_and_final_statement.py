import frappe
from frappe.utils import flt
from hrms.hr.doctype.full_and_final_statement.full_and_final_statement import (
    FullandFinalStatement,
    get_account_and_amount as original_get_account_and_amount,
)


class CustomFullAndFinalStatement(FullandFinalStatement):
    def get_payable_component(self):
        components = super().get_payable_component()
        if "Employee Severance Amount" not in components:
            components.append("Employee Severance Amount")
        return components

    @frappe.whitelist()
    def create_journal_entry(self):
        jv = super().create_journal_entry()

        severance_accounts = {
            row.account: row.amount
            for row in self.payables
            if row.reference_document_type == "Employee Severance Amount" and row.account
        }

        for account_row in jv.accounts:
            if account_row.account in severance_accounts:
                account_row.party_type = "Employee"
                account_row.party = self.employee

        return jv


@frappe.whitelist()
def custom_get_account_and_amount(ref_doctype, ref_document, company):
    if ref_doctype == "Employee Severance Amount":
        # 1. Fetch only severance_amount from your custom DocType
        amount = frappe.db.get_value("Employee Severance Amount", ref_document, "severance_amount")
        
        # 2. Get the default payroll payable account from Company settings
        payable_account = frappe.get_cached_value("Company", company, "default_payroll_payable_account")
        
        # 3. Return as [account, amount] array expected by the frontend JS
        return [payable_account, amount]

    # Fall back to standard HRMS method
    return original_get_account_and_amount(ref_doctype, ref_document, company)