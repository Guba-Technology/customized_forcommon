import frappe
from frappe import _
from hrms.hr.doctype.employee_advance.employee_advance import EmployeeAdvance


class CustomEmployeeAdvance(EmployeeAdvance):
    def validate(self):
        """Override to set advance_account based on custom_advance_type"""

        # --- Fetch company default accounts ---
        company_defaults = frappe.db.get_value(
            "Company",
            self.company,
            [
                "default_employee_advance_account",
                "custom_default_account_for_purchaser_advance",
                "custom_default_petty_cash_account",
                "custom_default_account_for_service_advance",
            ],
            as_dict=True,
        )

        # --- Select account based on custom_advance_type ---
        advance_account = None
        missing_account_label = None

        if self.custom_advance_type == "For Employee Advance":
            advance_account = company_defaults.default_employee_advance_account
            missing_account_label = "Employee Advance"
        elif self.custom_advance_type == "For Purchase":
            advance_account = company_defaults.custom_default_account_for_purchaser_advance
            missing_account_label = "Purchaser"
        elif self.custom_advance_type == "For Petty Cash":
            advance_account = company_defaults.custom_default_petty_cash_account
            missing_account_label = "Petty Cash"
        elif self.custom_advance_type == "For Service":
            advance_account = company_defaults.custom_default_account_for_service_advance
            missing_account_label = "Service"

        # --- If not found, raise a clear error message ---
        if not advance_account:
            frappe.throw(
                _("Please set the default account for {0} in the Company settings.").format(
                    missing_account_label
                ),
                title=_("Missing Account"),
            )

        # --- Set the account before the original logic runs ---
        self.advance_account = advance_account

        # --- Run original validation logic ---
        super().validate()


@frappe.whitelist()
def create_return_through_additional_salary(doc):
	import json

	if isinstance(doc, str):
		doc = frappe._dict(json.loads(doc))

	additional_salary = frappe.new_doc("Additional Salary")
	additional_salary.employee = doc.employee
	additional_salary.currency = doc.currency
	additional_salary.overwrite_salary_structure_amount = 0
	additional_salary.amount = doc.paid_amount - doc.claimed_amount - doc.return_amount
	additional_salary.company = doc.company
	additional_salary.ref_doctype = doc.doctype
	additional_salary.ref_docname = doc.name

	return additional_salary
