import frappe
from frappe import scrub
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry
from erpnext.accounts.doctype.invoice_discounting.invoice_discounting import get_party_account_based_on_invoice_discounting
from erpnext.accounts.doctype.payment_entry.payment_entry import get_outstanding_reference_documents
from frappe.utils import comma_or, flt
from frappe import _
class CustomPaymentEntry(PaymentEntry):
    def get_valid_reference_doctypes(self):
        if self.party_type == "Customer":
            return ("Sales Order", "Sales Invoice", "Journal Entry", "Dunning", "Payment Entry","Payment Request",)
        elif self.party_type == "Supplier":
            return ("Purchase Order", "Purchase Invoice", "Journal Entry", "Payment Entry","Payment Request","Payment Request",)
        elif self.party_type == "Shareholder":
            return ("Journal Entry","Payment Request",)
        elif self.party_type == "Employee":
            return ("Journal Entry","Payment Request","Employee Advance")
    def validate_reference_documents(self):
        valid_reference_doctypes = self.get_valid_reference_doctypes()
        if not valid_reference_doctypes:
            return

        for d in self.get("references"):
            if not d.allocated_amount:
                continue

            # ✅ Skip validation for Payment Request
            if d.reference_doctype == "Payment Request":
                continue

            if d.reference_doctype not in valid_reference_doctypes:
                frappe.throw(
                    _("Reference Doctype must be one of {0}").format(
                        comma_or(_(dt) for dt in valid_reference_doctypes)
                    )
                )

            if not d.reference_name:
                continue

            if not frappe.db.exists(d.reference_doctype, d.reference_name):
                frappe.throw(_("{0} {1} does not exist").format(d.reference_doctype, d.reference_name))

            ref_doc = frappe.get_doc(d.reference_doctype, d.reference_name)

            if d.reference_doctype != "Journal Entry":
                if self.party != ref_doc.get(scrub(self.party_type)):
                    frappe.throw(
                        _("{0} {1} is not associated with {2} {3}").format(
                            _(d.reference_doctype), d.reference_name, _(self.party_type), self.party
                        )
                    )
            else:
                self.validate_journal_entry()

            if d.reference_doctype in frappe.get_hooks("invoice_doctypes"):
                if self.party_type == "Customer":
                    ref_party_account = (
                        get_party_account_based_on_invoice_discounting(d.reference_name)
                        or ref_doc.get("debit_to")
                    )
                elif self.party_type == "Supplier":
                    ref_party_account = ref_doc.get("credit_to")
                elif self.party_type == "Employee":
                    ref_party_account = ref_doc.get("payable_account")
                else:
                    ref_party_account = None

                if (
                    ref_party_account != self.party_account
                    and not self.book_advance_payments_in_separate_party_account
                ):
                    frappe.throw(
                        _("{0} {1} is associated with {2}, but Party Account is {3}").format(
                            _(d.reference_doctype),
                            d.reference_name,
                            ref_party_account,
                            self.party_account,
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
        if self.references:
            uniq_vouchers = set([(x.reference_doctype, x.reference_name) for x in self.references])
            vouchers = [frappe._dict({"voucher_type": x[0], "voucher_no": x[1]}) for x in uniq_vouchers]
            latest_references = get_outstanding_reference_documents(
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

            # Group latest_references by (voucher_type, voucher_no)
            latest_lookup = {}
            for d in latest_references:
                d = frappe._dict(d)
                latest_lookup.setdefault((d.voucher_type, d.voucher_no), frappe._dict())[d.payment_term] = d

            for idx, d in enumerate(self.get("references"), start=1):
                # ✅ Skip validation for Payment Request
                if d.reference_doctype == "Payment Request":
                    continue

                latest = latest_lookup.get((d.reference_doctype, d.reference_name)) or frappe._dict()

                if (
                    d.payment_term is None or d.payment_term == ""
                ) and self.term_based_allocation_enabled_for_reference(d.reference_doctype, d.reference_name):
                    frappe.throw(
                        _(
                            "{0} has Payment Term based allocation enabled. Select a Payment Term for Row #{1} in Payment References section"
                        ).format(frappe.bold(d.reference_name), frappe.bold(idx))
                    )

                latest = latest.get(d.payment_term) or latest.get(None)

                if not latest:
                    frappe.throw(
                        _("{0} {1} has already been fully paid.").format(
                            _(d.reference_doctype), d.reference_name
                        )
                    )
                elif (
                    latest.outstanding_amount < latest.invoice_amount
                    and flt(d.outstanding_amount, d.precision("outstanding_amount"))
                    != flt(latest.outstanding_amount, d.precision("outstanding_amount"))
                    and d.payment_term == ""
                ):
                    frappe.throw(
                        _(
                            "{0} {1} has already been partly paid. Please use the 'Get Outstanding Invoice' or the 'Get Outstanding Orders' button to get the latest outstanding amounts."
                        ).format(_(d.reference_doctype), d.reference_name)
                    )

                fail_message = _("Row #{0}: Allocated Amount cannot be greater than outstanding amount.")

                if (
                    d.payment_term
                    and (
                        (flt(d.allocated_amount)) > 0
                        and latest.payment_term_outstanding
                        and (flt(d.allocated_amount) > flt(latest.payment_term_outstanding))
                    )
                    and self.term_based_allocation_enabled_for_reference(
                        d.reference_doctype, d.reference_name
                    )
                ):
                    frappe.throw(
                        _(
                            "Row #{0}: Allocated amount:{1} is greater than outstanding amount:{2} for Payment Term {3}"
                        ).format(d.idx, d.allocated_amount, latest.payment_term_outstanding, d.payment_term)
                    )

                if (flt(d.allocated_amount)) > 0 and flt(d.allocated_amount) > flt(latest.outstanding_amount):
                    frappe.throw(fail_message.format(d.idx))

                if flt(d.allocated_amount) < 0 and flt(d.allocated_amount) < flt(latest.outstanding_amount):
                    frappe.throw(fail_message.format(d.idx))