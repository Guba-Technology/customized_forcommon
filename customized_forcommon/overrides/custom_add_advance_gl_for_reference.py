import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry

def custom_add_advance_gl_for_reference(self, gl_entries, invoice):
    # If the account is NOT Receivable / Payable, skip party fields
    if self.party_account_type not in ["Receivable", "Payable"]:
        self.party_type = None
        self.party = None

    args_dict = {
        "party_type": self.party_type,
        "party": self.party,
        "account_currency": self.party_account_currency,
        "cost_center": self.cost_center,
        "voucher_type": "Payment Entry",
        "voucher_no": self.name,
        "voucher_detail_no": invoice.name,
    }

    if invoice.reconcile_effect_on:
        posting_date = invoice.reconcile_effect_on
    else:
        from erpnext.accounts.utils import get_reconciliation_effect_date

        posting_date = get_reconciliation_effect_date(
            invoice.reference_doctype, invoice.reference_name, self.company, self.posting_date
        )
        frappe.db.set_value("Payment Entry Reference", invoice.name, "reconcile_effect_on", posting_date)

    dr_or_cr, account = self.get_dr_and_account_for_advances(invoice)
    base_allocated_amount = self.calculate_base_allocated_amount_for_reference(invoice)
    args_dict["account"] = account
    args_dict[dr_or_cr] = base_allocated_amount
    args_dict[dr_or_cr + "_in_account_currency"] = invoice.allocated_amount
    args_dict[dr_or_cr + "_in_transaction_currency"] = (
        invoice.allocated_amount
        if self.party_account_currency == self.transaction_currency
        else base_allocated_amount / self.transaction_exchange_rate
    )

    args_dict.update(
        {
            "against_voucher_type": invoice.reference_doctype,
            "against_voucher": invoice.reference_name,
            "advance_voucher_type": invoice.advance_voucher_type,
            "advance_voucher_no": invoice.advance_voucher_no,
            "posting_date": posting_date,
        }
    )
    gle = self.get_gl_dict(args_dict, item=self)
    gl_entries.append(gle)

    # second GL entry
    args_dict[dr_or_cr] = 0
    args_dict[dr_or_cr + "_in_account_currency"] = 0
    dr_or_cr = "debit" if dr_or_cr == "credit" else "credit"
    args_dict["account"] = self.party_account
    args_dict[dr_or_cr] = base_allocated_amount
    args_dict[dr_or_cr + "_in_account_currency"] = invoice.allocated_amount
    args_dict[dr_or_cr + "_in_transaction_currency"] = (
        invoice.allocated_amount
        if self.party_account_currency == self.transaction_currency
        else base_allocated_amount / self.transaction_exchange_rate
    )

    args_dict.update(
        {
            "against_voucher_type": "Payment Entry",
            "against_voucher": self.name,
            "advance_voucher_type": invoice.advance_voucher_type,
            "advance_voucher_no": invoice.advance_voucher_no,
        }
    )
    gle = self.get_gl_dict(args_dict, item=self)
    gl_entries.append(gle)
