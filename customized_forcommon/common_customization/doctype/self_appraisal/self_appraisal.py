# Copyright (c) 2026, guba and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SelfAppraisal(Document):
	def validate(self):
		self.validate_employee_status()
		#self.validate_duplicated_criteria_entry()
		self.validate_weight_and_score()
		self.validate_duplicated_self_appraisal()
	
	def validate_employee_status(self):
		employee = frappe.get_doc("Employee", self.employee)
		if employee.status != "Active":
			frappe.throw(f"Employee <b> {self.employee} </b> is not Active")
	def validate_duplicated_criteria_entry(self):
		if self.self_evaluation_result:
			criterias = set()
			for row in self.self_evaluation_result:
				criteria = row.criteria
				if criteria in criterias:
					frappe.throw(f"<b>{criteria} </b> is already added")
				criterias.add(criteria)
	def validate_weight_and_score(self):
		if self.self_evaluation_result:
			total_weight = 0
			total_score = 0
			for i, row in enumerate(self.self_evaluation_result, start=1):
				weight = row.per_weightage
				score = float(row.custom_score)
				if score > weight:
					frappe.throw(f"Score ({score}) cannot exceed weight ({weight}) at row {i}")
				total_score += score
				self.total_score = total_score
				total_weight += weight
			if total_weight > 100:
				frappe.throw(f"Total weight ({total_weight}) cannot exceed 100%")
			if total_weight < 100:
				frappe.throw(f"Total weight ({total_weight}) must be a total of 100%")

	def validate_duplicated_self_appraisal(self):
		existing = frappe.get_all(
			"Self Appraisal",
			filters={
				"name": ["!=", self.name],
				"employee": self.employee,
				"appraisal": self.appraisal,
				"docstatus": ["!=", 2]
			},
		)
		if existing:
			frappe.throw(f"There is an existing self appraisal for employee <b>{self.employee}</b> in this appraisal")

	def on_submit(self):
		
		appraisal_doc = frappe.get_doc("Appraisal",self.appraisal)

		appraisal_doc.set("self_ratings", [])

		for row in self.self_evaluation_result:
			appraisal_doc.append("self_ratings", {
				"criteria": row.criteria,
				"per_weightage": row.per_weightage,  
				"custom_score": row.custom_score
			})
		appraisal_doc.reflections = self.reflection
		appraisal_doc.self_score = self.total_score
		appraisal_doc.save()
		link = f"<a href='/app/appraisal/{appraisal_doc.name}'>{appraisal_doc.name}</a>"
		frappe.msgprint(
			f"Self Appraisal Scores added to Appraisal ({link})",
			title="Appraisal Updated",
			indicator="green",
			is_minimizable=True
		)
	@frappe.whitelist()
	def set_feedback_criteria(self):
		if not self.appraisal:
			return

		template = frappe.db.get_value("Appraisal", self.appraisal, "appraisal_template")
		template = frappe.get_doc("Appraisal Template", template)

		self.set("self_evaluation_result", [])
		for entry in template.rating_criteria:
			self.append(
				"self_evaluation_result",
				{
					"criteria": entry.criteria,
					"per_weightage": entry.per_weightage,
				},
			)

		return self