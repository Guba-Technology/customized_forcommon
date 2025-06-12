from frappe import _
import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry, get_party_account, get_account_currency
from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest

logger = frappe.logger("payment_request")

class CustomPaymentRequest(PaymentRequest):

    def validate(self):
        logger.info(f"[{self.name}] Starting validate()")
        try:
            if self.get("__islocal"):
                self.status = "Draft"
                logger.info(f"[{self.name}] Status set to Draft for new document")

            if not self.party_type or not self.party:
                frappe.throw(_("Party Type and Party are required."))

            if not self.currency:
                frappe.throw(_("Currency must be specified."))

            if not self.company:
                frappe.throw(_("Company must be specified."))

            if self.reference_doctype and self.reference_name:
                logger.info(f"[{self.name}] Validating reference document: {self.reference_doctype} - {self.reference_name}")
                super().validate_reference_document()
                super().validate_payment_request_amount()

            super().validate_subscription_details()
            logger.info(f"[{self.name}] Validation complete")

        except Exception as e:
            logger.error(f"[{self.name}] Validation failed: {e}")
            frappe.log_error(frappe.get_traceback(), _("Validation failed in CustomPaymentRequest"))
            raise

    def before_submit(self):
        logger.info(f"[{self.name}] Running before_submit()")
        try:
            if not self.reference_doctype and not self.reference_name:
                self.outstanding_amount = self.grand_total
                logger.info(f"[{self.name}] No reference set; outstanding_amount = grand_total: {self.grand_total}")
            else:
                super().before_submit()
                logger.info(f"[{self.name}] Called super().before_submit()")

        except Exception as e:
            logger.error(f"[{self.name}] Error in before_submit: {e}")
            frappe.log_error(frappe.get_traceback(), _("Error in before_submit"))
            raise

    def on_submit(self):
        logger.info(f"[{self.name}] Running on_submit()")
        try:
            self.db_set("reference_doctype", "Payment Request")
            self.db_set("reference_name", self.name)
            logger.info(f"[{self.name}] Reference doctype and name set to self")

            if self.payment_request_type == "Outward":
                self.db_set("status", "Initiated")
                logger.info(f"[{self.name}] Status set to Initiated (Outward)")
                return
            elif self.payment_request_type == "Inward":
                self.db_set("status", "Requested")
                logger.info(f"[{self.name}] Status set to Requested (Inward)")

            if not self.reference_doctype or not self.reference_name:
                logger.info(f"[{self.name}] No reference document to process")
                return

            send_mail = super().payment_gateway_validation() if self.payment_gateway else None
            logger.info(f"[{self.name}] payment_gateway_validation result: {send_mail}")

            ref_doc = frappe.get_doc(self.reference_doctype, self.reference_name)

            if (getattr(ref_doc, "order_type", None) == "Shopping Cart") or self.flags.get("mute_email"):
                send_mail = False

            if send_mail and self.payment_channel != "Phone":
                logger.info(f"[{self.name}] Sending email notification")
                super().set_payment_request_url()
                super().send_email()
                super().make_communication_entry()
            elif self.payment_channel == "Phone":
                logger.info(f"[{self.name}] Phone payment requested")
                super().request_phone_payment()

        except Exception as e:
            logger.error(f"[{self.name}] Error in on_submit: {e}")
            frappe.log_error(frappe.get_traceback(), _("Error in CustomPaymentRequest.on_submit"))
            raise

    def on_cancel(self):
        logger.info(f"[{self.name}] Running on_cancel()")
        try:
            self.db_set("reference_doctype", None)
            self.db_set("reference_name", None)
            super().on_cancel()
            logger.info(f"[{self.name}] Cancel process complete")

        except Exception as e:
            logger.error(f"[{self.name}] Error in on_cancel: {e}")
            frappe.log_error(frappe.get_traceback(), _("Error in CustomPaymentRequest.on_cancel"))
            raise

    def create_payment_entry(self, submit=True):
        logger.info(f"[{self.name}] Creating Payment Entry, submit={submit}")
        try:
            frappe.flags.ignore_account_permission = True

            if self.reference_doctype == "Payment Request":
                ref_doc = self

                if not self.party_type or not self.party:
                    frappe.throw(_("Party Type and Party are required in Payment Request"))

                party_account = get_party_account(self.party_type, self.party, self.company)
            else:
                ref_doc = frappe.get_doc(self.reference_doctype, self.reference_name)

                if self.reference_doctype in ["Sales Invoice", "POS Invoice"]:
                    party_account = ref_doc.debit_to
                elif self.reference_doctype == "Purchase Invoice":
                    party_account = ref_doc.credit_to
                else:
                    party_account = get_party_account("Customer", ref_doc.get("customer"), ref_doc.company)

            party_account_currency = (
                self.get("party_account_currency")
                or ref_doc.get("party_account_currency")
                or get_account_currency(party_account)
            )

            party_amount = bank_amount = self.outstanding_amount or self.grand_total
            company_currency = frappe.get_cached_value("Company", self.company, "default_currency")

            if party_account_currency == company_currency and party_account_currency != self.currency:
                exchange_rate = ref_doc.get("conversion_rate") or 1
                if not exchange_rate:
                    frappe.throw(_("Missing conversion rate to compute bank amount."))
                bank_amount = flt(party_amount / exchange_rate, self.precision("grand_total"))

            logger.info(f"[{self.name}] party_amount={party_amount}, bank_amount={bank_amount}")

            if self.reference_doctype == "Payment Request":
                payment_type = "Receive" if self.payment_request_type == "Inward" else "Pay"

                # if not self.payment_account:
                #     frappe.throw(_("Payment Account is required to create Payment Entry."))

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

                if self.currency != ref_doc.company_currency:
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
                logger.info(f"[{self.name}] Payment Entry {payment_entry.name} created and submitted")

            return payment_entry

        except Exception as e:
            logger.error(f"[{self.name}] Error creating Payment Entry: {e}")
            frappe.log_error(frappe.get_traceback(), _("Error while creating Payment Entry from Payment Request"))
            raise

