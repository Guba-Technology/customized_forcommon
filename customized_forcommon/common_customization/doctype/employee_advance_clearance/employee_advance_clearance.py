# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today

class EmployeeAdvanceClearance(Document):
	def validate(self):
		# Calculate unpaid amount
		if self.advance_amount and self.returned_amount is not None:
			self.unreturned_amount = self.advance_amount - self.returned_amount
		else:
			self.unreturned_amount = self.advance_amount  # fallback if returned_amount not set
		self.difference_amount = self.invoiced_amount - self.unreturned_amount

	


	def on_submit(self):
		self.create_journal_entry()
	def on_cancel(self):
		self.cancel_journal_entry()
	def on_trash(self):
		pass

	def create_journal_entry(self):
		# Check if unpaid amount matches invoiced amount for notification
		if self.unreturned_amount != self.invoiced_amount:
			diff_for_msg = self.unreturned_amount - self.invoiced_amount
			frappe.msgprint(
				msg="There is a mismatch of {:,.2f} between unpaid amount and invoiced amount.".format(diff_for_msg),
				indicator="orange"
			)

		# 1. create a new Journal Entry
		journal_entry = frappe.new_doc("Journal Entry")
		journal_entry.voucher_type = "Journal Entry"
		journal_entry.company = self.company
		journal_entry.posting_date = today()

		# Initialize logic variables
		difference = 0
		amount = 0

		if self.unreturned_amount and self.invoiced_amount:
			if self.invoiced_amount > self.unreturned_amount:
				# Invoice is larger than advance
				amount = self.unreturned_amount
				difference = self.invoiced_amount - self.unreturned_amount
			
			elif self.invoiced_amount == self.unreturned_amount:
				# When equal, we use invoiced_amount to clear the advance
				amount = self.invoiced_amount
				difference = 0  # No difference to record
			
			else:
				# Invoice is smaller than advance
				amount = self.invoiced_amount
				difference = 0

		# Row 1: Difference Account (Credit)
		# Only added if there is an actual remainder
		if difference > 0:
			journal_entry.append("accounts", {
				"account": self.difference_account,
				"party_type": "Supplier",
				"party": self.supplier,
				"credit_in_account_currency": difference,
				"debit_in_account_currency": 0
			})

		# Row 2: Purchase Invoice Detail (Debit)
		journal_entry.append("accounts", {
			"account": self.payable_account,
			"party_type": "Supplier",
			"party": self.supplier,
			"credit_in_account_currency": 0,
			"debit_in_account_currency": self.invoiced_amount,
			"reference_type": "Purchase Invoice",
			"reference_name": self.purchase_invoice
		})

		# Row 3: Employee Advance Detail (Credit)
		# This clears the actual Employee Advance document
		if amount > 0:
			journal_entry.append("accounts", {
				"account": self.advance_account,
				"party_type": "Employee",
				"party": self.employee,
				"credit_in_account_currency": amount,
				"debit_in_account_currency": 0,
				"reference_type": "Employee Advance",
				"reference_name": self.employee_advance
			})
		
		journal_entry.insert()
		
		# Update your custom DocType fields
		self.db_set("created_journal_entry", journal_entry.name)
		self.db_set("difference_of_invoice_and_advance_amount", difference)
		self.db_set("status", "Cleared")
		
		journal_entry.submit()
		
		# UI link for the user
		link = frappe.utils.get_link_to_form("Journal Entry", journal_entry.name)
		frappe.msgprint(f"Journal Entry {link} is successfully created")

	def cancel_journal_entry(self):
		if not self.created_journal_entry:
			frappe.msgprint("No linked Journal Entry to cancel.")
			return

		try:
			journal_entry = frappe.get_doc("Journal Entry", self.created_journal_entry)
			if journal_entry.docstatus == 1:
				journal_entry.cancel()
				self.db_set("status", "Cancelled")

				frappe.msgprint(f"Linked Journal Entry {journal_entry.name} has been cancelled.")
			else:
				frappe.msgprint(f"Journal Entry {journal_entry.name} is already cancelled or in draft.")
		except frappe.DoesNotExistError:
			frappe.msgprint(f"Journal Entry {self.created_journal_entry} not found.")

	
