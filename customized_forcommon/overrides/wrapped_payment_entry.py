import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry as OriginalPaymentEntry
from hrms.overrides.employee_payment_entry import EmployeePaymentEntry
from customized_forcommon.overrides.payment_entry import CustomPaymentEntry

class WrappedPaymentEntry(OriginalPaymentEntry):
    def _get_delegate_cls(self):
        """Determine delegate class based on current references"""
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
        elif has_payment_request:
            return CustomPaymentEntry
        return None

    def _delegate_method(self, method_name, *args, **kwargs):
        """Delegate method call to appropriate class if exists"""
        delegate_cls = self._get_delegate_cls()
        if delegate_cls and hasattr(delegate_cls, method_name):
            method = getattr(delegate_cls, method_name)
            return method(self, *args, **kwargs)
        return super().method_name(*args, **kwargs)

    def get_valid_reference_doctypes(self):
        return self._delegate_method('get_valid_reference_doctypes')

    def validate_reference_documents(self):
        return self._delegate_method('validate_reference_documents')

    def validate_allocated_amount_with_latest_data(self):
        return self._delegate_method('validate_allocated_amount_with_latest_data')

    def set_missing_ref_details(self, *args, **kwargs):
        return self._delegate_method('set_missing_ref_details', *args, **kwargs)

    def get_reference_party_account(self, *args, **kwargs):
        return self._delegate_method('get_reference_party_account', *args, **kwargs)
