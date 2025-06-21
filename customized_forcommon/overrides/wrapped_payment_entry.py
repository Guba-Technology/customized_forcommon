import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry as OriginalPaymentEntry
from hrms.overrides.employee_payment_entry import EmployeePaymentEntry
from customized_forcommon.overrides.payment_entry import CustomPaymentEntry

class WrappedPaymentEntry(OriginalPaymentEntry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Prevent infinite recursion if already one of the special subclasses
        if isinstance(self, (EmployeePaymentEntry, CustomPaymentEntry)):
            self._resolved = self
        else:
            self._resolved = self._resolve_delegate()

    def _resolve_delegate(self):
        references = self.get("references") or []

        has_employee_doc = any(
            ref.reference_doctype in ("Expense Claim", "Employee Advance", "Gratuity")
            for ref in references
        )
        has_payment_request = any(ref.reference_doctype == "Payment Request" for ref in references)

        if has_employee_doc:
            return EmployeePaymentEntry(self)
        elif has_payment_request:
            return CustomPaymentEntry(self)
        return self  # use original if no special references

    # Delegate methods
    def get_valid_reference_doctypes(self):
        if hasattr(self._resolved, "get_valid_reference_doctypes"):
            return self._resolved.get_valid_reference_doctypes()
        return super().get_valid_reference_doctypes()

    def validate_reference_documents(self):
        if hasattr(self._resolved, "validate_reference_documents"):
            return self._resolved.validate_reference_documents()
        return super().validate_reference_documents()

    def validate_allocated_amount_with_latest_data(self):
        if hasattr(self._resolved, "validate_allocated_amount_with_latest_data"):
            return self._resolved.validate_allocated_amount_with_latest_data()
        return super().validate_allocated_amount_with_latest_data()

    def set_missing_ref_details(self, *args, **kwargs):
        if hasattr(self._resolved, "set_missing_ref_details"):
            return self._resolved.set_missing_ref_details(*args, **kwargs)
        return super().set_missing_ref_details(*args, **kwargs)

    def get_reference_party_account(self, *args, **kwargs):
        if hasattr(self._resolved, "get_reference_party_account"):
            return self._resolved.get_reference_party_account(*args, **kwargs)
        return super().get_reference_party_account(*args, **kwargs)
