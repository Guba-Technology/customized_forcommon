# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StudentReport(Document):
	def on_submit(self):
		result = frappe.db.sql(
			"""SELECT education_program FROM `tabTraining Commitment` WHERE employee = %s""",
			(self.employee,),
			as_dict=True
		)

		if not result:
			frappe.throw(f"No training commitment found for employee {self.employee}")

		program = result[0].education_program
		if program.strip().lower() != "summer":
			frappe.throw("Only Summer programs are allowed")


	pass
