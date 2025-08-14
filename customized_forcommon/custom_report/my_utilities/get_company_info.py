import frappe

class GetCompanyInfo:
    def __init__(self, Company = None):
        self.Company = Company or frappe.defaults.get_user_default("Company")
    def get_custom_field(self, fieldname):
        """Generic method to fetch any custom field from Company."""
        if not self.Company:
            frappe.throw("Default company not set for current user.")
        return frappe.db.get_value("Company", self.Company, fieldname)
    def get_vat_payable_account(self):
        return self.get_custom_field("custom_vat_payable_account")
    def get_vat_receivable_account(self):
        return self.get_custom_field("custom_vat_receivable_account")
    def get_withholding_payable_account(self):
        return self.get_custom_field("custom_withholding_payable_account")
    def get_withholding_receivable_account(self):
        return self.get_custom_field("custom_withholding_receivable_account")
    def get_pension_payable_account(self):
        return self.get_custom_field("custom_pension_payable_account")
    def get_pension_receivable_account(self):
        return self.get_custom_field("custom_pension_receivable_account")
    