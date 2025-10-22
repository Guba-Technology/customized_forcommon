# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StudentReport(Document):
	def validate(self):
		if self.status =="" or self.status == None:
			self.status = "Pending"
	def before_submit(self):
		self.status = "Submitted"
	def on_submit(self):
		result = frappe.db.sql(
			"""SELECT education_program FROM `tabTraining Commitment` WHERE employee = %s""",
			(self.employee,),
			as_dict=True
		)

		if not result:
			frappe.throw(f"No training commitment found for employee {self.employee}")

		


	pass
