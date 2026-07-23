# Copyright (c) 2026, Guba Technology and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LCMaster(Document):
	def validate(self):
		self.validate_duplicated_account()

	def validate_duplicated_account(self):
		accounts = {}

		for i, row in enumerate(self.cif_value_accounts, start=1):
			account = row.cif_value_account

			if not account:
				continue

			if account in accounts:
				frappe.throw(
					f"CIF Value Account <b>{account}</b> is already added in row "
					f"<b>{accounts[account]}</b>. Duplicate found in row <b>{i}</b>."
				)

			accounts[account] = i


