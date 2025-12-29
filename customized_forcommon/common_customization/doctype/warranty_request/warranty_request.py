# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today

class WarrantyRequest(Document):
	def validate(self):
		self.validate_duplicated_request_per_employee()
		self.validate_duplicated_witness()
		self.validate_income()
		self.validate_guarantor_age()
		self.restrict_self_not_to_be_witness()
		
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
	def validate_duplicated_witness(self):
		if self.witnesses:
			witnesses_emp = set()
			for row in self.witnesses:
				employee = row.employee
				if employee and employee in witnesses_emp:
					frappe.throw(f"{employee} already added as a witness")
				witnesses_emp.add(employee)
	def validate_income(self):
		if self.warranty_request_for == "Self":
			if self.daily_income and self.annual_income:
				if self.annual_income <= self.daily_income:
					frappe.throw("Annual Income cannot be less than or equal to Daily Income")

	def validate_guarantor_age(self):
		if self.warranty_request_for == "Self" and self.guarantor_date_of_birth:
			today_date = getdate(today())
			birth_date = getdate(self.guarantor_date_of_birth)

			# Calculate age in years
			age = (today_date - birth_date).days / 365.25

			if age < 18:
				frappe.throw(_("Guarantor must be at least 18 years of age."))
	def restrict_self_not_to_be_witness(self):
		if self.warranty_request_for == "Self":
			if self.witnesses:
				for row in self.witnesses:
					if row.employee == self.employee:
						frappe.throw("Employee cannot be a witness for him/herself")
