# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class EmployeeAdvanceClearance(Document):
	def validate(self):
		if self.advance_amount != self.invoiced_amount:
			difference = self.advance_amount - self.invoiced_amount
			frappe.msgprint(f"There is a remaining amount of {difference} in the employee advance")

		
	def on_submit(self):
		self.create_journal_entry()
	def before_cancel(self):
		pass
	def on_trash(self):
		pass

	def create_journal_entry(self):
		# 1. create a new Journal Entry with type "Journal Entry"
		journal_entry = frappe.new_doc("Journal Entry")
		journal_entry.voucher_type = "Journal Entry"
		journal_entry.company = self.company
		journal_entry.posting_date = today()

		if self.advance_amount and self.invoiced_amount:
			difference = self.advance_amount - self.invoiced_amount
			if difference > 0:
				advance_amount = self.invoiced_amount
			elif difference == 0:
				advance_amount = self.advance_amount
		
		# 2. Append Purchase Invoice Detail in Accounting Entries
		journal_entry.append("accounts", {
			"account": self.payable_account,
			"party_type": "Supplier",
			"party": self.supplier,
			"credit_in_account_currency": 0,
			"debit_in_account_currency":  self.invoiced_amount,
			"reference_type": "Purchase Invoice",
			"reference_name": self.purchase_invoice
		})
		# 3. Append Employee Advance Detail in Accounting Entries
		journal_entry.append("accounts", {
			"account": self.advance_account,
			"party_type": "Employee",
			"party": self.employee,
			"credit_in_account_currency": advance_amount,
			"debit_in_account_currency": 0,
			"reference_type": "Employee Advance",
			"reference_name": self.employee_advance
		})
		
		journal_entry.insert()
		self.db_set("created_journal_entry", journal_entry.name)
		self.db_set("difference_of_invoice_and_advance_amount", difference)
		journal_entry.submit()
		frappe.db.commit()
		link = "".join([f'<a href="/app/journal-entry/{journal_entry.name}" style="text-decoration: underline" target=_blank >{journal_entry.name}</a>'])
		frappe.msgprint(f"Journal Entry {link} is successfully created")

	
