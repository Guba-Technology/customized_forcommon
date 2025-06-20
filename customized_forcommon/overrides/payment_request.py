from frappe import _, _
import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions
from erpnext.accounts.doctype.payment_entry.payment_entry import (
    get_payment_entry, get_party_account, get_account_currency
)
from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest

logger = frappe.logger("payment_request")

class CustomPaymentRequest(PaymentRequest):

    def log_error(self, msg, e):
        logger.error(f"[{self.name}] {msg}: {e}")
        frappe.log_error(frappe.get_traceback(), _(msg))

    def validate(self):
        logger.info(f"[{self.name}] Starting validate()")
        try:
            if self.get("__islocal"):
                self.status = "Draft"
                logger.info(f"[{self.name}] Status set to Draft")

            required_fields = ["party_type", "party", "currency", "company"]
            for field in required_fields:
                if not self.get(field):
                    frappe.throw(_("{0} must be specified.").format(_(field.replace("_", " ").title())))

            if self.reference_doctype and self.reference_name:
                logger.info(f"[{self.name}] Validating reference: {self.reference_doctype} - {self.reference_name}")
                super().validate_reference_document()
                super().validate_payment_request_amount()

            super().validate_subscription_details()
            logger.info(f"[{self.name}] Validation complete")

        except Exception as e:
            self.log_error("Validation failed in CustomPaymentRequest", e)
            raise

    def before_submit(self):
        logger.info(f"[{self.name}] Running before_submit()")
        try:
            if not self.reference_doctype and not self.reference_name:
                self.outstanding_amount = self.grand_total
                logger.info(f"[{self.name}] No reference; outstanding_amount = grand_total: {self.grand_total}")
            else:
                super().before_submit()
        except Exception as e:
            self.log_error("Error in before_submit", e)
            raise

    def on_submit(self):
        logger.info(f"[{self.name}] Running on_submit()")
        try:
            if not self.reference_doctype and not self.reference_name:
                self.db_set("reference_doctype", "Payment Request")
                self.db_set("reference_name", self.name)

            status = "Initiated" if self.payment_request_type == "Outward" else "Requested"
            self.db_set("status", status)
            logger.info(f"[{self.name}] Status set to {status}")

            if not self.reference_doctype or not self.reference_name:
                return

            send_mail = super().payment_gateway_validation() if self.payment_gateway else None
            logger.info(f"[{self.name}] payment_gateway_validation result: {send_mail}")

            ref_doc = frappe.get_doc(self.reference_doctype, self.reference_name)
            send_mail = send_mail and not getattr(ref_doc, "order_type", "") == "Shopping Cart"
            send_mail = send_mail and not self.flags.get("mute_email")

            if send_mail and self.payment_channel != "Phone":
                logger.info(f"[{self.name}] Sending email")
                super().set_payment_request_url()
                super().send_email()
                super().make_communication_entry()
            elif self.payment_channel == "Phone":
                logger.info(f"[{self.name}] Phone payment triggered")
                super().request_phone_payment()

        except Exception as e:
            self.log_error("Error in CustomPaymentRequest.on_submit", e)
            raise

    def on_cancel(self):
        logger.info(f"[{self.name}] Running on_cancel()")
        try:
            if self.reference_doctype == "Payment Request":
                self.db_set("reference_doctype", None)
                self.db_set("reference_name", None)
            super().on_cancel()
        except Exception as e:
            self.log_error("Error in CustomPaymentRequest.on_cancel", e)
            raise

    def create_payment_entry(self, submit=True):
        logger.info(f"[{self.name}] Creating Payment Entry, submit={submit}")
        try:
            frappe.flags.ignore_account_permission = True

            ref_doc = self if self.reference_doctype == "Payment Request" else frappe.get_doc(self.reference_doctype, self.reference_name)

            if not self.party_type or not self.party:
                frappe.throw(_("Party Type and Party are required in Payment Request"))

            party_account = (
                get_party_account(self.party_type, self.party, self.company)
                if self.reference_doctype == "Payment Request"
                else self._get_party_account_from_reference(ref_doc)
            )

            party_account_currency = (
                self.get("party_account_currency")
                or ref_doc.get("party_account_currency")
                or get_account_currency(party_account)
            )

            party_amount = bank_amount = self.outstanding_amount or self.grand_total
            company_currency = frappe.get_cached_value("Company", self.company, "default_currency")

            if party_account_currency == company_currency and party_account_currency != self.currency:
                exchange_rate = ref_doc.get("conversion_rate") or 1
                bank_amount = flt(party_amount / exchange_rate, self.precision("grand_total"))

            logger.info(f"[{self.name}] party_amount={party_amount}, bank_amount={bank_amount}")

            if self.reference_doctype == "Payment Request":
                payment_type = "Receive" if self.payment_request_type == "Inward" else "Pay"
                payment_entry = frappe.new_doc("Payment Entry")
                payment_entry.update({
                    "payment_type": payment_type,
                    "company": self.company,
                    "party_type": self.party_type,
                    "party": self.party,
                    "paid_from": self.payment_account if payment_type == "Pay" else party_account,
                    "paid_to": party_account if payment_type == "Pay" else self.payment_account,
                    "paid_amount": party_amount,
                    "received_amount": bank_amount,
                    "source_exchange_rate": 1,
                    "target_exchange_rate": 1,
                    "mode_of_payment": self.mode_of_payment,
                    "reference_no": self.name,
                    "reference_date": nowdate(),
                    "remarks": f"Payment Entry from Payment Request {self.name}",
                    "project": self.get("project"),
                    "cost_center": self.get("cost_center")
                })
                payment_entry.append("references", {
                    "reference_doctype": "Payment Request",
                    "reference_name": self.name,
                    "total_amount": self.grand_total,
                    "outstanding_amount": self.outstanding_amount,
                    "allocated_amount": party_amount,
                    "payment_request": self.name,
                })
            else:
                payment_entry = get_payment_entry(
                    self.reference_doctype,
                    self.reference_name,
                    party_amount=party_amount,
                    bank_account=self.payment_account,
                    bank_amount=bank_amount,
                    created_from_payment_request=True,
                )
                payment_entry.update({
                    "mode_of_payment": self.mode_of_payment,
                    "reference_no": self.name,
                    "reference_date": nowdate(),
                    "remarks": f"Payment Entry against {self.reference_doctype} {self.reference_name} via Payment Request {self.name}",
                    "cost_center": self.get("cost_center"),
                    "project": self.get("project"),
                })
                self._allocate_payment_request_to_pe_references(references=payment_entry.references)

                if self.currency != ref_doc.get("company_currency"):
                    if (
                        self.payment_request_type == "Outward"
                        and payment_entry.paid_from_account_currency == ref_doc.company_currency
                        and payment_entry.paid_from_account_currency != payment_entry.paid_to_account_currency
                    ):
                        payment_entry.paid_amount = payment_entry.base_paid_amount = (
                            payment_entry.target_exchange_rate * payment_entry.received_amount
                        )

            for dimension in get_accounting_dimensions():
                payment_entry.update({dimension: self.get(dimension)})

            if submit:
                payment_entry.insert(ignore_permissions=True)
                payment_entry.submit()
                logger.info(f"[{self.name}] Payment Entry {payment_entry.name} submitted")

            return payment_entry

        except Exception as e:
            self.log_error("Error while creating Payment Entry", e)
            raise

    def _get_party_account_from_reference(self, ref_doc):
        if self.reference_doctype in ["Sales Invoice", "POS Invoice"]:
            return ref_doc.debit_to
        elif self.reference_doctype == "Purchase Invoice":
            return ref_doc.credit_to
        return get_party_account("Customer", ref_doc.get("customer"), ref_doc.company)
