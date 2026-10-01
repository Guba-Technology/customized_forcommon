# Copyright (c) 2026, Guba Technology
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document


class TrainingImpactAssessment(Document):
	def validate(self):
		self.validate_assigned_employees()

	def validate_assigned_employees(self):
		seen = set()
		for row in self.assigned_employees:
			if not row.employee:
				frappe.throw(_("Row #{0}: Employee is mandatory").format(row.idx))
			if row.employee in seen:
				frappe.throw(
					_("Row #{0}: Employee {1} is already assigned to this Training Impact Assessment").format(
						row.idx, row.employee
					)
				)
			seen.add(row.employee)

	@frappe.whitelist()
	def create_assessment_responses(self):
		
		if not self.assessment_template:
			frappe.throw(_("Please set an Assessment Template before creating responses"))

		if not self.assigned_employees:
			frappe.throw(_("Please assign at least one Employee before creating responses"))

		template = frappe.get_doc("Training Assessment Template", self.assessment_template)

		created = []
		skipped = []

		for row in self.assigned_employees:
			# Trainee response - evaluator is the employee themselves
			result = self._create_single_response(
				trainee=row.employee, evaluator=row.employee, evaluator_type="Trainee", template=template
			)
			(created if result else skipped).append(f"{row.employee_name or row.employee} (Trainee)")

			# Manager response - evaluator is the employee's manager
			if row.manager:
				result = self._create_single_response(
					trainee=row.employee, evaluator=row.manager, evaluator_type="Manager", template=template
				)
				(created if result else skipped).append(f"{row.employee_name or row.employee} (Manager)")
			else:
				skipped.append(f"{row.employee_name or row.employee} (Manager - no manager set)")

		message = ""
		if created:
			message += _("Created responses for: {0}").format(", ".join(created)) + "<br>"
		if skipped:
			message += _("Skipped (already exists or no manager): {0}").format(", ".join(skipped))

		frappe.msgprint(message or _("No new responses were created."), title=_("Training Assessment Response"))

		return {"created": created, "skipped": skipped}

	def _create_single_response(self, trainee, evaluator, evaluator_type, template):
		"""Create one Training Assessment Response if it does not already exist."""
		exists = frappe.db.exists(
			"Training Assessment Response",
			{
				"training_impact_assessment": self.name,
				"trainee_name": trainee,
				"evaluator_type": evaluator_type,
			},
		)
		if exists:
			return None

		response = frappe.new_doc("Training Assessment Response")
		response.trainee_name = trainee
		response.evaluator = evaluator
		response.evaluator_type = evaluator_type
		response.training_impact_assessment = self.name
		response.assessment_date = self.training_date
		response.status = "Draft"

		for criteria_row in template.criteria:
			response.append(
				"assessment_criteria",
				{
					"criteria": criteria_row.criteria,
				},
			)

		response.insert(ignore_permissions=True)
		return response.name
