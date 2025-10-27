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

        if self.custom_advance_type == "For Employee Advance":
            advance_account = company_defaults.default_employee_advance_account
        elif self.custom_advance_type == "For Purchase":
            advance_account = company_defaults.custom_default_account_for_purchaser_advance
        elif self.custom_advance_type == "For Petty Cash":
            advance_account = company_defaults.custom_default_petty_cash_account
        elif self.custom_advance_type == "For Service":
            advance_account = company_defaults.custom_default_account_for_service_advance

        # --- If not found, raise an error ---
        if not advance_account:
            frappe.throw(
                _("Please set the default account for '{0}' in the Company settings.").format(
                    self.custom_advance_type
                ),
                title=_("Missing Account"),
            )

        # --- Set the account before original logic runs ---
        self.advance_account = advance_account

        # --- Now call the original validate logic ---
        super().validate()

        frappe.msgprint(
            _("Advance Account automatically set to: {0}").format(self.advance_account)
        )
