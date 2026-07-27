import frappe
from frappe.utils import flt
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import (
    PurchaseInvoice as BasePurchaseInvoice,
)


class CustomPurchaseInvoice(BasePurchaseInvoice):
    def get_gl_entries(self, warehouse_account=None):
        gl_entries = super().get_gl_entries(warehouse_account)

        if not self.custom_project_advance_payment:
            return gl_entries

        self.update_gl_entries(gl_entries)
        return gl_entries

    def update_gl_entries(self, gl_entries):
        pap = frappe.get_doc(
            "Project Advance Payment", self.custom_project_advance_payment
        )
        if not pap.created_advance_payment_entry and not pap.advance_paid:
            frappe.throw(f"Please make an advance payment first in Project Advance Payment: <b>{pap.name}</b>")

        advance_account = pap.account_for_advance
        advance_percent = flt(pap.advance_percent)

        if advance_percent <= 0 or not advance_account:
            return

        total = flt(self.grand_total)
        recovered_amount = (total * advance_percent) / 100.0

        if recovered_amount <= 0:
            return

        creditors_account = self.credit_to

        # 1. Reduce the credit_to entry by recovered_amount
        for gle in gl_entries:
            if gle.account == creditors_account and flt(gle.credit) > 0:
                gle.credit -= recovered_amount
                gle.credit_in_account_currency -= recovered_amount
                break

        # 2. Credit the advance account for recovered_amount
        gl_entries.append(
            self.get_gl_dict(
                {
                    "account": advance_account,
                    "party_type": "Supplier",
                    "party": self.supplier,
                    "credit": recovered_amount,
                    "credit_in_account_currency": recovered_amount,
                    "remarks": self.remarks or f"Project Advance Recovery ({advance_percent}%)",
                },
                self.party_account_currency,
                item=self,
            )
        )

    def set_status(self, update=False, status=None, update_modified=True):
        """Override status calculation to handle custom net payable balance dynamic updates."""
        super().set_status(update=update, status=status, update_modified=update_modified)

        if self.docstatus == 1 and self.custom_project_advance_payment:
            pap = frappe.get_doc(
                "Project Advance Payment", self.custom_project_advance_payment
            )
            advance_percent = flt(pap.advance_percent)
            recovered_amount = (flt(self.grand_total) * advance_percent) / 100.0
            
            # The net amount actually payable to supplier
            net_payable = flt(self.grand_total) - recovered_amount

            # Fetch total payments allocated via Payment Entries against this Purchase Invoice
            actual_paid = flt(
                frappe.db.sql(
                    """
                    SELECT SUM(allocated_amount) 
                    FROM `tabPayment Entry Reference`
                    WHERE reference_doctype = 'Purchase Invoice'
                      AND reference_name = %s
                      AND docstatus = 1
                    """,
                    self.name,
                )[0][0]
                or 0.0
            )

            # Calculate remaining balance left to pay
            outstanding = max(0.0, net_payable - actual_paid)

            # Determine real status based on payments
            if outstanding <= 0:
                new_status = "Paid"
            elif actual_paid > 0:
                new_status = "Partly Paid"
            else:
                new_status = "Unpaid"

            # Update DB directly so ERPNext UI and reports reflect the accurate status
            self.db_set("outstanding_amount", outstanding)
            self.db_set("status", new_status)