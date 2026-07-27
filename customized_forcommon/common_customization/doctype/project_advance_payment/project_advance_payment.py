# Copyright (c) 2026, Guba Technology and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class ProjectAdvancePayment(Document):
	def validate(self):
		if not self.account_for_advance:
			frappe.throw(f"Account for Advance cannot be empty. Please set in company: <b> {self.company}</b> ")
		self.validate_duplicated_terms()
		self.calculate_advance_amount()
		self.validate_term_percentage()
		self.calculate_term_amount()
	
	def validate_duplicated_terms(self):
		terms = {}

		for i, row in enumerate(self.payment_terms, start=1):
			term = row.payment_term

			if not term:
				continue

			if term in terms:
				frappe.throw(
					f"Payment Term <b>{term}</b> is already added in row "
					f"<b>{terms[term]}</b>. Duplicate found in row <b>{i}</b>."
				)

			terms[term] = i


	def calculate_advance_amount(self):
		if self.advance_percent > 100:
			frappe.throw("Advance Percent cannot be more than 100%")
		contract_value = self.contract_value or 0
		advance_percent  =self.advance_percent or 0
		advance_amount = contract_value * advance_percent /100
		self.advance_amount  = advance_amount

	def validate_term_percentage(self):
		total_percentage = 0
		if self.payment_terms:
			for row in self.payment_terms:
				percentage = row.percent
				total_percentage += percentage
		if total_percentage > 100:
			frappe.throw("Total percent of the payment terms cannot be more than 100")
		elif total_percentage < 100:
			frappe.throw("Total percent of the payment terms must be 100")

	def calculate_term_amount(self):
		contract_value = self.contract_value or 0
		if self.payment_terms:
			for row in self.payment_terms:
				row.amount = contract_value * row.percent / 100

	def on_cancel(self):
		self.cancel_linked_purchase_invoices()
		self.cancel_linked_payment_entries()


	def cancel_linked_payment_entries(self):
		payment_entries = frappe.get_all(
			"Payment Entry",
			filters={
				"custom_project_advance_payment": self.name,
				"docstatus": 1
			},
			fields=["name"]
		)

		for row in payment_entries:
			payment = frappe.get_doc(
				"Payment Entry",
				row.name
			)

			payment.cancel()
	
	def cancel_linked_purchase_invoices(self):
		purchase_invoices = frappe.get_all(
			"Purchase Invoice",
			filters={
				"custom_project_advance_payment": self.name,
				"docstatus": 1
			},
			fields=["name"]
		)

		for pi in purchase_invoices:
			purchase = frappe.get_doc(
				"Purchase Invoice",
				pi.name
			)

			purchase.cancel()



	



@frappe.whitelist()
def make_payment_entry(source_name):
	doc = frappe.get_doc("Project Advance Payment", source_name)

	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = "Pay"
	pe.party_type = "Supplier"
	pe.party = doc.contractor
	pe.paid_amount = doc.advance_amount
	pe.paid_from_account_currency = doc.currency
	pe.paid_to_account_currency = doc.currency
	pe.paid_to = doc.account_for_advance
	pe.custom_project_advance_payment = doc.name

	if doc.purchase_tax_template:
		pe.purchase_taxes_and_charges_template = doc.purchase_tax_template

		template = frappe.get_doc(
			"Purchase Taxes and Charges Template",
			doc.purchase_tax_template
		)
		for tax in template.taxes:
			row = pe.append("taxes", {})
			row.add_deduct_tax = "Add"
			row.charge_type = "On Paid Amount"
			row.account_head = tax.account_head
			row.description = tax.description
			row.rate = tax.rate
			row.tax_amount = pe.paid_amount * tax.rate / 100 
			row.tax_amount = pe.paid_amount * tax.rate / 100 
			row.total = pe.paid_amount + (pe.paid_amount * tax.rate / 100)


	return pe

@frappe.whitelist()
def make_purchase_invoice(source_name, payment_term, rate):
	# Fetch parent document
	doc = frappe.get_doc("Project Advance Payment", source_name)

	# Initialize Purchase Invoice doc
	pi = frappe.new_doc("Purchase Invoice")
	pi.company = doc.company
	pi.supplier = doc.contractor
	pi.custom_project_advance_payment = doc.name
	pi.custom_project_advance_payment_term = payment_term

	# Append child table item seamlessly
	if doc.purchase_item:
		pi.append("items", {
			"item_code": doc.purchase_item,
			"qty": 1,
			"rate": flt(rate),
		})
	if doc.purchase_tax_template:
		pi.taxes_and_charges = doc.purchase_tax_template
			

	# Run standard Frappe triggers to calculate taxes, totals, and missing defaults
	pi.set_missing_values()

	# Return as dict so client can render form
	return pi.as_dict()