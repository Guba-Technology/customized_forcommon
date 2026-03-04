# your_app/your_app/doctype/custom_payment_request/custom_payment_request.py

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils import flt, nowdate
from erpnext.accounts.doctype.payment_entry.payment_entry import (
    get_payment_entry,
    get_party_account,
    get_account_currency,
)
from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest

logger = frappe.logger("payment_request")


class CustomPaymentRequest(PaymentRequest):
    def validate(self):
        logger.info(f"[{self.name or 'New'}] validate() started")

        if self.is_new():
            self.status = "Draft"

        # === Internal Transfer: No Party Needed ===
        if self.payment_request_type == "Internal Transfer":
            if not self.payment_account:
                frappe.throw(_("From Account (Payment Account) is required for Internal Transfer"))
            if not self.get("paid_to"):
                frappe.throw(_("To Account is required for Internal Transfer"))
        else:
            # Inward / Outward
            if not self.party_type or not self.party:
                frappe.throw(_("Party Type and Party are required"))

        if not self.currency or not self.company:
            frappe.throw(_("Currency and Company are required"))

        # Auto-set conversion rate
        company_currency = frappe.get_cached_value("Company", self.company, "default_currency")
        if self.currency != company_currency and not self.conversion_rate:
            rate = frappe.db.get_value(
                "Currency Exchange",
                {"from_currency": self.currency, "to_currency": company_currency},
                "exchange_rate",
            )
            self.conversion_rate = rate or 1

        if self.reference_doctype and self.reference_name:
            super().validate_reference_document()
            super().validate_payment_request_amount()

        super().validate_subscription_details()
        logger.info(f"[{self.name or 'New'}] validate() completed")

    def before_submit(self):
        if not self.reference_doctype and not self.reference_name:
            self.outstanding_amount = flt(self.grand_total)

    def on_submit(self):
        logger.info(f"[{self.name}] on_submit()")

        # Only set self-reference if standalone
        if not self.reference_doctype and not self.reference_name:
            self.db_set("reference_doctype", "Payment Request")
            self.db_set("reference_name", self.name)

        # Set correct status
        if self.payment_request_type in ["Outward", "Internal Transfer"]:
            self.db_set("status", "Initiated")
        else:  # Inward
            self.db_set("status", "Requested")

        # Internal Transfer → no email
        if self.payment_request_type == "Internal Transfer":
            return

        # Inward with gateway → send email
        if self.payment_request_type == "Inward" and self.payment_gateway and self.payment_channel != "Phone":
            if not self.flags.get("mute_email"):
                self.set_payment_request_url()
                self.send_email()
                self.make_communication_entry()

    def on_cancel(self):
        if self.reference_doctype == "Payment Request" and self.reference_name == self.name:
            self.db_set({"reference_doctype": None, "reference_name": None})
        super().on_cancel()

    def create_payment_entry(self, submit=True):
        logger.info(f"[{self.name}] create_payment_entry(submit={submit})")

        frappe.flags.ignore_account_permission = True
        amount = flt(self.outstanding_amount or self.grand_total)
        company_currency = frappe.get_cached_value("Company", self.company, "default_currency")

        # === INTERNAL TRANSFER ===
        if self.payment_request_type == "Internal Transfer":
            return self._create_internal_transfer_pe(amount, submit)

        # === STANDALONE INWARD / OUTWARD (no reference doc) ===
        if self.reference_doctype == "Payment Request" and self.reference_name == self.name:
            return self._create_standalone_pe(amount, submit)

        # === FROM INVOICE / OTHER DOCTYPE ===
        return self._create_from_reference_pe(amount, submit, company_currency)

    def _create_internal_transfer_pe(self, amount, submit):
        from_account = self.payment_account
        to_account = self.paid_to

        if not from_account or not to_account:
            frappe.throw(_("From and To accounts are required for Internal Transfer"))

        pe = frappe.new_doc("Payment Entry")
        pe.update({
            "payment_type": "Internal Transfer",
            "company": self.company,
            "posting_date": nowdate(),
            "paid_from": from_account,
            "paid_to": to_account,
            "paid_amount": amount,
            "received_amount": amount,
            "mode_of_payment": self.mode_of_payment,
            "reference_no": self.name,
            "reference_date": nowdate(),
            "remarks": f"Internal Transfer - {self.name}",
            "cost_center": self.cost_center,
            "project": self.project,
        })

        # Handle multi-currency
        from_curr = frappe.db.get_value("Account", from_account, "account_currency")
        to_curr = frappe.db.get_value("Account", to_account, "account_currency")

        if from_curr != self.currency:
            pe.paid_amount = flt(amount * (self.conversion_rate or 1))
            pe.source_exchange_rate = pe.paid_amount / amount

        if to_curr != self.currency:
            pe.received_amount = flt(amount * (self.conversion_rate or 1))
            pe.target_exchange_rate = pe.received_amount / amount

        # pe.append("references", {
        #     "reference_doctype": "Payment Request",
        #     "reference_name": self.name,
        #     "allocated_amount": amount
        # })

        if submit:
            pe.insert(ignore_permissions=True)
            pe.submit()
            self.db_set("status", "Paid")
            self.notify_update()
            frappe.msgprint(_("Internal Transfer completed: {0}").format(pe.name_link()), indicator="green")

        return pe

    def _create_standalone_pe(self, amount, submit):
        party_account = get_party_account(self.party_type, self.party, self.company)
        bank_account = self.payment_account

        if not bank_account:
            frappe.throw(_("Payment Account is required"))

        payment_type = "Receive" if self.payment_request_type == "Inward" else "Pay"
        paid_from = bank_account if payment_type == "Pay" else party_account
        paid_to = party_account if payment_type == "Pay" else bank_account

        pe = frappe.new_doc("Payment Entry")
        pe.update({
            "payment_type": payment_type,
            "company": self.company,
            "posting_date": nowdate(),
            "party_type": self.party_type,
            "party": self.party,
            "paid_from": paid_from,
            "paid_to": paid_to,
            "paid_amount": amount,
            "received_amount": amount,
            "mode_of_payment": self.mode_of_payment,
            "reference_no": self.name,
            "reference_date": nowdate(),
            "remarks": f"Payment via Request {self.name}",
        })

        pe.append("references", {
            "reference_doctype": "Payment Request",
            "reference_name": self.name,
            "total_amount": self.grand_total,
            "outstanding_amount": amount,
            "allocated_amount": amount,
        })

        if submit:
            pe.insert(ignore_permissions=True)
            pe.submit()
            self.db_set("status", "Paid")
            self.notify_update()

        return pe

    def _create_from_reference_pe(self, amount, submit, company_currency):
        pe = get_payment_entry(
            self.reference_doctype,
            self.reference_name,
            party_amount=amount,
            bank_account=self.payment_account,
            bank_amount=amount,
        )

        pe.update({
            "mode_of_payment": self.mode_of_payment,
            "reference_no": self.name,
            "reference_date": nowdate(),
            "remarks": f"Via Payment Request {self.name}",
            "cost_center": self.cost_center,
            "project": self.project,
        })

        if submit:
            pe.insert(ignore_permissions=True)
            pe.submit()

        return pe