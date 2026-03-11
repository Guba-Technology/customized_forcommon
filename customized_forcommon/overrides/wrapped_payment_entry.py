import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry as OriginalPaymentEntry
from hrms.overrides.employee_payment_entry import EmployeePaymentEntry
from customized_forcommon.overrides.payment_entry import CustomPaymentEntry


class WrappedPaymentEntry(OriginalPaymentEntry):
    """
    Hybrid PaymentEntry override that safely delegates logic
    to HRMS or Custom Payment Request overrides.
    """

    # -------------------------------------------------------------------------
    # Delegate resolution
    # -------------------------------------------------------------------------
    def _get_delegate_cls(self):
        references = self.get("references") or []

        has_employee_doc = any(
            ref.reference_doctype in ("Expense Claim", "Employee Advance", "Gratuity")
            for ref in references
        )

        has_payment_request = any(
            ref.reference_doctype == "Payment Request"
            for ref in references
        )

        if has_employee_doc:
            return EmployeePaymentEntry

        if has_payment_request:
            return CustomPaymentEntry

        return None

    # -------------------------------------------------------------------------
    # Core safety layer (ERPNext v15 requirement)
    # -------------------------------------------------------------------------
    def _ensure_core_payment_entry_fields(self):
        """
        Ensure ERPNext-required attributes exist before any delegated logic runs.
        Prevents:
            AttributeError: 'NoneType' object has no attribute 'lower'
        """

        # --- Paid From / Paid To account currencies ---
        if self.paid_from and not getattr(self, "paid_from_account_currency", None):
            self.paid_from_account_currency = frappe.db.get_value(
                "Account", self.paid_from, "account_currency"
            )

        if self.paid_to and not getattr(self, "paid_to_account_currency", None):
            self.paid_to_account_currency = frappe.db.get_value(
                "Account", self.paid_to, "account_currency"
            )

        # --- party_account_currency (CRITICAL) ---
        if not getattr(self, "party_account_currency", None):
            if self.payment_type == "Receive":
                self.party_account_currency = self.paid_from_account_currency
            else:
                self.party_account_currency = self.paid_to_account_currency

        # --- Absolute fallback ---
        if not self.party_account_currency:
            self.party_account_currency = frappe.get_cached_value(
                "Company", self.company, "default_currency"
            )

        # --- Correct account type for suppliers (defensive fix) ---
        if self.party_type == "Supplier" and self.paid_to_account_type == "Receivable":
            self.paid_to_account_type = "Payable"

    # -------------------------------------------------------------------------
    # Delegation handler
    # -------------------------------------------------------------------------
    def _delegate_method(self, method_name, *args, **kwargs):
        # 🔒 Guarantee ERPNext-required fields first
        self._ensure_core_payment_entry_fields()

        delegate_cls = self._get_delegate_cls()

        if delegate_cls:
            delegate_method = getattr(delegate_cls, method_name, None)
            if callable(delegate_method):
                return delegate_method(self, *args, **kwargs)

        parent_method = getattr(super(), method_name, None)
        if callable(parent_method):
            return parent_method(*args, **kwargs)

        frappe.throw(f"Method '{method_name}' not found in delegate or parent class.")

    # -------------------------------------------------------------------------
    # Delegated ERPNext hooks
    # -------------------------------------------------------------------------
    #def before_validate(self):
    #    return self._delegate_method("before_validate")

    def get_valid_reference_doctypes(self):
        return self._delegate_method("get_valid_reference_doctypes")

    def validate_reference_documents(self):
        return self._delegate_method("validate_reference_documents")

    def validate_allocated_amount_with_latest_data(self):
        return self._delegate_method("validate_allocated_amount_with_latest_data")

    def set_missing_ref_details(self, *args, **kwargs):
        return self._delegate_method("set_missing_ref_details", *args, **kwargs)

    def get_reference_party_account(self, *args, **kwargs):
        return self._delegate_method("get_reference_party_account", *args, **kwargs)
