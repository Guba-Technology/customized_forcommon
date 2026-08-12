# Copyright (c) 2026, Guba Technology and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SalaryPaymentDistributionRequest(Document):
	def validate(self):
		if self.cash_amount <= 0:
			frappe.throw(_("Cash Amount must be greater than zero."))

		if self.effective_to and self.effective_to < self.effective_from:
			frappe.throw(_("Effective To cannot be before Effective From."))

		employee_company = frappe.db.get_value(
			"Employee",
			self.employee,
			"company"
		)

		if employee_company != self.company:
			frappe.throw(
				_("Employee {0} does not belong to Company {1}.")
				.format(self.employee, self.company)
			)
