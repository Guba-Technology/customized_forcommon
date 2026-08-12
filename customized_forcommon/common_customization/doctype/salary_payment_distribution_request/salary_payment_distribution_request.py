import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class SalaryPaymentDistributionRequest(Document):
	def validate(self):
		self.validate_company()
		self.validate_duplicated_employee()

	def validate_company(self):
		if self.cash_amount <= 0:
			frappe.throw(_("Cash Amount must be greater than zero."))

		if self.effective_to and getdate(self.effective_to) < getdate(self.effective_from):
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

	def validate_duplicated_employee(self):
		current_from = getdate(self.effective_from)
		current_to = getdate(self.effective_to) if self.effective_to else None

		existing_requests = frappe.get_all(
			"Salary Payment Distribution Request",
			filters={
				"employee": self.employee,
				"company": self.company,
				"name": ["!=", self.name],
				"docstatus": ["!=", 2],
			},
			fields=[
				"name",
				"effective_from",
				"effective_to",
			],
		)

		for request in existing_requests:
			existing_from = getdate(request.effective_from)
			existing_to = (
				getdate(request.effective_to)
				if request.effective_to
				else None
			)

			# Existing request is open-ended
			if not existing_to:
				if not current_to or existing_from <= current_to:
					frappe.throw(
						_(
							"Employee {0} already has a Salary Payment "
							"Distribution Request {1} whose effective "
							"period overlaps with this request."
						).format(self.employee, request.name)
					)

			# Current request is open-ended
			elif not current_to:
				if existing_to >= current_from:
					frappe.throw(
						_(
							"Employee {0} already has a Salary Payment "
							"Distribution Request {1} whose effective "
							"period overlaps with this request."
						).format(self.employee, request.name)
					)

			# Both requests have an end date
			elif (
				existing_from <= current_to
				and existing_to >= current_from
			):
				frappe.throw(
					_(
						"Employee {0} already has a Salary Payment "
						"Distribution Request {1} whose effective "
						"period overlaps with this request."
					).format(self.employee, request.name)
				)