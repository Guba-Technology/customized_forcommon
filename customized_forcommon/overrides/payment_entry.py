import frappe
from frappe import _, scrub
from frappe.utils import comma_or, flt
from erpnext.accounts.doctype.payment_entry.payment_entry import (
    PaymentEntry, get_outstanding_reference_documents
)
from erpnext.accounts.doctype.invoice_discounting.invoice_discounting import (
    get_party_account_based_on_invoice_discounting
)

class CustomPaymentEntry(PaymentEntry):

    def has_payment_request_reference(self):
        return any(d.reference_doctype == "Payment Request" for d in self.get("references", []))

    def get_valid_reference_doctypes(self):
        if not self.has_payment_request_reference():
            return super().get_valid_reference_doctypes()

        return {
            "Customer": ("Sales Order", "Sales Invoice", "Journal Entry", "Dunning", "Payment Entry", "Payment Request"),
            "Supplier": ("Purchase Order", "Purchase Invoice", "Journal Entry", "Payment Entry", "Payment Request"),
            "Shareholder": ("Journal Entry", "Payment Request"),
            "Employee": ("Journal Entry", "Payment Request", "Employee Advance"),
        }.get(self.party_type, ())

    def validate_reference_documents(self):
        if not self.has_payment_request_reference():
            return super().validate_reference_documents()

        valid_doctypes = self.get_valid_reference_doctypes()
        if not valid_doctypes:
            return

        for d in self.get("references"):
            if not d.allocated_amount or d.reference_doctype == "Payment Request":
                continue

            if d.reference_doctype not in valid_doctypes:
                frappe.throw(
                    _("Reference Doctype must be one of {0}").format(
                        comma_or([_(dt) for dt in valid_doctypes])
                    )
                )

            if not d.reference_name or not frappe.db.exists(d.reference_doctype, d.reference_name):
                frappe.throw(_("{0} {1} does not exist").format(d.reference_doctype, d.reference_name))

            ref_doc = frappe.get_doc(d.reference_doctype, d.reference_name)

            if d.reference_doctype != "Journal Entry" and self.party != ref_doc.get(scrub(self.party_type)):
                frappe.throw(
                    _("{0} {1} is not associated with {2} {3}").format(
                        _(d.reference_doctype), d.reference_name, _(self.party_type), self.party
                    )
                )

            if d.reference_doctype == "Journal Entry":
                self.validate_journal_entry()

            if d.reference_doctype in frappe.get_hooks("invoice_doctypes"):
                ref_party_account = self.get_reference_party_account(ref_doc, d.reference_doctype, d.reference_name)

                if ref_party_account != self.party_account and not self.book_advance_payments_in_separate_party_account:
                    frappe.throw(
                        _("{0} {1} is associated with account {2}, but Party Account is {3}").format(
                            _(d.reference_doctype), d.reference_name, ref_party_account, self.party_account
                        )
                    )

                if d.reference_doctype == "Purchase Invoice" and ref_doc.get("on_hold"):
                    frappe.throw(
                        _("{0} {1} is on hold").format(_(d.reference_doctype), d.reference_name),
                        title=_("Invalid Purchase Invoice"),
                    )

            if ref_doc.docstatus != 1:
                frappe.throw(
                    _("{0} {1} must be submitted").format(_(d.reference_doctype), d.reference_name)
                )

    def validate_allocated_amount_with_latest_data(self):
        if not self.has_payment_request_reference():
            return super().validate_allocated_amount_with_latest_data()

        if not self.references:
            return

        vouchers = [
            frappe._dict({"voucher_type": x.reference_doctype, "voucher_no": x.reference_name})
            for x in self.references
        ]
        latest_refs = get_outstanding_reference_documents(
            {
                "posting_date": self.posting_date,
                "company": self.company,
                "party_type": self.party_type,
                "payment_type": self.payment_type,
                "party": self.party,
                "party_account": self.paid_from if self.payment_type == "Receive" else self.paid_to,
                "get_outstanding_invoices": True,
                "get_orders_to_be_billed": True,
                "vouchers": vouchers,
                "book_advance_payments_in_separate_party_account": self.book_advance_payments_in_separate_party_account,
            },
            validate=True,
        )

        latest_lookup = self._group_latest_references(latest_refs)

        for idx, d in enumerate(self.get("references"), start=1):
            if d.reference_doctype == "Payment Request":
                continue

            latest = latest_lookup.get((d.reference_doctype, d.reference_name), frappe._dict())
            latest_term_data = latest.get(d.payment_term) or latest.get(None)

            if not latest_term_data:
                frappe.throw(
                    _("{0} {1} has already been fully paid.").format(_(d.reference_doctype), d.reference_name)
                )

            if not d.payment_term and self.term_based_allocation_enabled_for_reference(d.reference_doctype, d.reference_name):
                frappe.throw(
                    _("{0} has Payment Term based allocation enabled. Select a Payment Term for Row #{1}.")
                    .format(frappe.bold(d.reference_name), frappe.bold(idx))
                )

            if d.payment_term and flt(d.allocated_amount) > flt(latest_term_data.payment_term_outstanding):
                frappe.throw(
                    _("Row #{0}: Allocated amount {1} is greater than outstanding {2} for Payment Term {3}")
                    .format(d.idx, d.allocated_amount, latest_term_data.payment_term_outstanding, d.payment_term)
                )

            if flt(d.allocated_amount) > flt(latest_term_data.outstanding_amount):
                frappe.throw(_("Row #{0}: Allocated Amount cannot be greater than outstanding amount.").format(d.idx))

            if flt(d.allocated_amount) < 0 and flt(d.allocated_amount) < flt(latest_term_data.outstanding_amount):
                frappe.throw(_("Row #{0}: Allocated Amount cannot be negative or exceed outstanding amount.").format(d.idx))

    def _group_latest_references(self, latest_refs):
        grouped = {}
        for d in latest_refs:
            d = frappe._dict(d)
            grouped.setdefault((d.voucher_type, d.voucher_no), {}).setdefault(d.payment_term, d)
        return grouped

    def get_reference_party_account(self, ref_doc, doctype, name):
        if self.party_type == "Customer":
            return get_party_account_based_on_invoice_discounting(name) or ref_doc.get("debit_to")
        elif self.party_type == "Supplier":
            return ref_doc.get("credit_to")
        elif self.party_type == "Employee":
            return ref_doc.get("payable_account")
        return None
