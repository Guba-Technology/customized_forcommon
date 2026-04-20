from frappe import _
import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
    get_accounting_dimensions
)
from erpnext.accounts.doctype.payment_entry.payment_entry import (
    get_payment_entry,
    get_party_account,
    get_account_currency,
)
from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest

logger = frappe.logger("payment_request")


class CustomPaymentRequest(PaymentRequest):

    # ----------------------------------------------------------------------
    # VALIDATE
    # ----------------------------------------------------------------------
    def validate(self):
        logger.info(f"[{self.name}] Starting validate()")

        try:
            if self.get("__islocal"):
                self.status = "Draft"
                logger.info(f"[{self.name}] Status set to Draft (new document)")

            if not self.currency:
                frappe.throw(_("Currency must be specified."))

            if not self.company:
                frappe.throw(_("Company must be specified."))

            # Party check EXCEPT Internal Transfer
            if self.payment_request_type != "Internal Transfer":
                if not self.party_type or not self.party:
                    frappe.throw(_("Party Type and Party are required."))

            # Validate reference
            if self.reference_doctype and self.reference_name:
                logger.info(
                    f"[{self.name}] Validating reference {self.reference_doctype}/{self.reference_name}"
                )
                super().validate_reference_document()
                super().validate_payment_request_amount()

            # Subscription validations
            super().validate_subscription_details()
            logger.info(f"[{self.name}] validate() completed")

        except Exception as e:
            logger.error(f"[{self.name}] Validation failed: {e}")
            frappe.log_error(frappe.get_traceback(), _("Validation Error in CustomPaymentRequest"))
            raise

    # ----------------------------------------------------------------------
    # BEFORE SUBMIT
    # ----------------------------------------------------------------------
    def before_submit(self):
        logger.info(f"[{self.name}] Running before_submit()")

        try:
            if not (self.reference_doctype and self.reference_name):
                self.outstanding_amount = self.grand_total
                logger.info(
                    f"[{self.name}] No reference → outstanding_amount = {self.grand_total}"
                )
                return

            super().before_submit()
            logger.info(f"[{self.name}] super().before_submit() executed")

        except Exception as e:
            logger.error(f"[{self.name}] Error in before_submit: {e}")
            frappe.log_error(frappe.get_traceback(), _("Error in before_submit"))
            raise

    # ----------------------------------------------------------------------
    # ON SUBMIT
    # ----------------------------------------------------------------------
    def on_submit(self):
        logger.info(f"[{self.name}] Running on_submit()")

        try:
            # Set reference to self when no reference
            if not (self.reference_doctype and self.reference_name):
                self.db_set("reference_doctype", "Payment Request")
                self.db_set("reference_name", self.name)
                logger.info(f"[{self.name}] Reference self-set")

            # Status logic
            if self.payment_request_type in ["Outward", "Internal Transfer"]:
                self.db_set("status", "Initiated")
            else:
                self.db_set("status", "Requested")

            # Payment gateway logic
            send_mail = super().payment_gateway_validation() if self.payment_gateway else None
            logger.info(f"[{self.name}] payment_gateway_validation: {send_mail}")

            ref_doc = frappe.get_doc(self.reference_doctype, self.reference_name)

            if (getattr(ref_doc, "order_type", None) == "Shopping Cart") or self.flags.get("mute_email"):
                send_mail = False

            # Email logic
            if send_mail and self.payment_channel != "Phone":
                super().set_payment_request_url()
                super().send_email()
                super().make_communication_entry()

            elif self.payment_channel == "Phone":
                super().request_phone_payment()

            logger.info(f"[{self.name}] on_submit() completed")

        except Exception as e:
            logger.error(f"[{self.name}] Error in on_submit: {e}")
            frappe.log_error(frappe.get_traceback(), _("Error in CustomPaymentRequest.on_submit"))
            raise

    # ----------------------------------------------------------------------
    # ON CANCEL
    # ----------------------------------------------------------------------
    def on_cancel(self):
        logger.info(f"[{self.name}] Running on_cancel()")

        try:
            self.db_set("reference_doctype", None)
            self.db_set("reference_name", None)
            super().on_cancel()
            logger.info(f"[{self.name}] on_cancel() completed")

        except Exception as e:
            logger.error(f"[{self.name}] Error in on_cancel: {e}")
            frappe.log_error(frappe.get_traceback(), _("Error in CustomPaymentRequest.on_cancel"))
            raise

    # ----------------------------------------------------------------------
    # CREATE PAYMENT ENTRY
    # ----------------------------------------------------------------------
    def create_payment_entry(self, submit=True):
        logger.info(f"[{self.name}] Creating Payment Entry (submit={submit})")

        try:
            frappe.flags.ignore_account_permission = True

            # ------------------------------------------------------------------
            # CASE 1: PAYMENT REQUEST ITSELF (NO EXTERNAL REFERENCE)
            # ------------------------------------------------------------------
            if self.reference_doctype == "Payment Request":

                # ==============================================================
                # INTERNAL TRANSFER
                # ==============================================================
                if self.payment_request_type == "Internal Transfer":
                    if not self.payment_account:
                        frappe.throw(_("Payment Account is required for Internal Transfer"))

                    company_currency = frappe.get_cached_value(
                        "Company", self.company, "default_currency"
                    )

                    payment_entry = frappe.new_doc("Payment Entry")
                    payment_entry.update({
                        "payment_type": "Internal Transfer",
                        "company": self.company,
                        "paid_from": self.payment_account,
                        "paid_to": self.payment_account,
                        "paid_amount": self.grand_total,
                        "received_amount": self.grand_total,
                        "paid_from_account_currency": company_currency,
                        "paid_to_account_currency": company_currency,
                        "party_account_currency": company_currency,
                        "source_exchange_rate": 1,
                        "target_exchange_rate": 1,
                        "mode_of_payment": self.mode_of_payment,
                        "reference_no": self.name,
                        "reference_date": nowdate(),
                        "remarks": f"Internal Transfer from Payment Request {self.name}",
                        "project": self.get("project"),
                        "cost_center": self.get("cost_center"),
                    })

                # ==============================================================
                # NORMAL PAYMENT REQUEST (INWARD / OUTWARD)
                # ==============================================================
                else:
                    if not self.party_type or not self.party:
                        frappe.throw(_("Party Type and Party are required"))

                    party_account = get_party_account(
                        self.party_type,
                        self.party,
                        self.company
                    )

                    party_account_currency = get_account_currency(party_account)
                    company_currency = frappe.get_cached_value(
                        "Company", self.company, "default_currency"
                    )

                    payment_type = "Receive" if self.payment_request_type == "Inward" else "Pay"

                    payment_entry = frappe.new_doc("Payment Entry")
                    payment_entry.update({
                        "payment_type": payment_type,
                        "company": self.company,
                        "party_type": self.party_type,
                        "party": self.party,
                        "paid_from": (
                            party_account if payment_type == "Receive"
                            else self.payment_account
                        ),
                        "paid_to": (
                            self.payment_account if payment_type == "Receive"
                            else party_account
                        ),
                        "paid_amount": self.grand_total,
                        "received_amount": self.grand_total,
                        "party_account_currency": party_account_currency,
                        "source_exchange_rate": 1,
                        "target_exchange_rate": 1,
                        "mode_of_payment": self.mode_of_payment,
                        "reference_no": self.name,
                        "reference_date": nowdate(),
                        "remarks": f"Payment Entry from Payment Request {self.name}",
                        "project": self.get("project"),
                        "cost_center": self.get("cost_center"),
                    })

                    payment_entry.append("references", {
                        "reference_doctype": "Payment Request",
                        "reference_name": self.name,
                        "total_amount": self.grand_total,
                        "outstanding_amount": self.outstanding_amount,
                        "allocated_amount": self.grand_total,
                        "payment_request": self.name,
                    })

            # ------------------------------------------------------------------
            # CASE 2: PAYMENT REQUEST AGAINST A DOCUMENT (SI / PI / etc.)
            # ------------------------------------------------------------------
            else:
                payment_entry = get_payment_entry(
                    self.reference_doctype,
                    self.reference_name,
                    party_amount=self.outstanding_amount,
                    bank_account=self.payment_account,
                    bank_amount=self.outstanding_amount,
                    created_from_payment_request=True,
                )

                payment_entry.update({
                    "mode_of_payment": self.mode_of_payment,
                    "reference_no": self.name,
                    "reference_date": nowdate(),
                    "remarks": (
                        f"Payment Entry against {self.reference_doctype} "
                        f"{self.reference_name} via Payment Request {self.name}"
                    ),
                    "project": self.get("project"),
                    "cost_center": self.get("cost_center"),
                })

                self._allocate_payment_request_to_pe_references(
                    references=payment_entry.references
                )

            # ------------------------------------------------------------------
            # ACCOUNTING DIMENSIONS
            # ------------------------------------------------------------------
            for dimension in get_accounting_dimensions():
                payment_entry.set(dimension, self.get(dimension))

            # ------------------------------------------------------------------
            # FINALIZE
            # ------------------------------------------------------------------
            if submit:
                payment_entry.insert(ignore_permissions=True)
                payment_entry.submit()

            logger.info(
                f"[{self.name}] Payment Entry {payment_entry.name} created successfully"
            )
            return payment_entry

        except Exception:
            logger.error(f"[{self.name}] Payment Entry creation failed")
            frappe.log_error(
                frappe.get_traceback(),
                _("Error while creating Payment Entry from Payment Request")
            )
            raise
