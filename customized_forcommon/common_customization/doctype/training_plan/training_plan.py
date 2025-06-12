# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TrainingPlan(Document):
	def validate(self):
		# Custom validation logic can be added here
		self.check_duplicate_department()
		self.check_duplicate_employee()
	def before_insert(self):
		# Custom logic before inserting the document
		if self.no_of_female_trainee and self.no_of_male_trainee:
			self.total_trainee = self.no_of_female_trainee + self.no_of_male_trainee

	def check_duplicate_employee(self):
		emp = set()
		if self.employee:
			for row in self.employee:
				if row.employee:
					if  row.employee in emp:
						frappe.throw(f"Duplicate Employee {row.employee} found")
					emp.add(row.employee)

	def check_duplicate_department(self):
		dept = set()
		if self.department:
			for row in self.department:
				if row.department:
					if row.department in dept:
						frappe.throw(f"Duplicate Department {row.department} found")
					dept.add(row.department)

			