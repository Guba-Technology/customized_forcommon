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
    def get_vat_openning(self, fiscal_year):
        vt_opening = frappe.db.get_value("VAT Closing", {"parent": self.Company, "fiscal_year": fiscal_year}, "vat_opening") or None
        # print("VAT Opening: ", vt_opening)
        # print("Fiscal Year: ", fiscal_year)
        if vt_opening:
            print("VAT Opening: ", vt_opening)
            return vt_opening
        return self.get_custom_field("custom_vat_openning_amount")
    def get_fiscal_year_start(self):
        query = "select name, year_start_date, year_end_date from `tabFiscal Year` order by year_start_date desc limit 1"
        fiscal_years = frappe.db.sql(query, as_dict=True)

        # print("Fiscal Year: ", fiscal_years[0].name)
        if fiscal_years:
            return fiscal_years[0].year_start_date, fiscal_years[0].name, fiscal_years[0].year_end_date


 