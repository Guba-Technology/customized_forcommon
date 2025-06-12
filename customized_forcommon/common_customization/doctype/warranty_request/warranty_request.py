# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class WarrantyRequest(Document):
	def validate(self):
		self.validate_duplicated_request_per_employee()

	def validate_duplicated_request_per_employee(self):
		"""Ensure that an employee cannot have multiple warranty requests"""
		if self.employee:
			existing_approved_requests = frappe.get_all(
				"Warranty Request",
				filters={
					"employee": self.employee,
					"status": "Active", # Only check for active requests
					"name": ["!=", self.name]  # Exclude current request
				},
				fields=["name"]
			)

			if existing_approved_requests:
				frappe.throw(
					_(f"An Active warranty request already exists for this employee {self.employee}.")
				)

			