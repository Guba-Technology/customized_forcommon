# Copyright (c) 2025, Guba Technology and Contributors

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class TrainingAssessmentResponse(Document):
	def validate(self):
		self.validate_assignment_membership()
		self.validate_duplicate_response()
		self.validate_evaluator()
		self.validate_score_ranges()
		self.validate_after_training_timing()
		if self.docstatus == 0 and self.status == "Submitted":
			# status should only say "Submitted" once actually submitted (docstatus 1)
			self.status = "Pending"

	def before_submit(self):
		self.validate_all_scores_present()
		self.status = "Submitted"

	def on_submit(self):
		from customized_forcommon.common_customization.doctype.training_impact_assessment_report.training_impact_assessment_report import (
			generate_report,
		)

		generate_report(self.training_impact_assessment)

	def on_cancel(self):
		self.status = "Draft"
		from customized_forcommon.common_customization.doctype.training_impact_assessment_report.training_impact_assessment_report import (
			generate_report,
		)

		generate_report(self.training_impact_assessment)

	def validate_duplicate_response(self):

		existing = frappe.db.exists(
			"Training Assessment Response",
			{
				"training_impact_assessment": self.training_impact_assessment,
				"trainee_name": self.trainee_name,
				"evaluator_type": self.evaluator_type,
				"name": ["!=", self.name or ""],
				"docstatus": ["!=", 2],
			},
		)
		if existing:
			frappe.throw(
				_(
					"A {0} response already exists for Employee {1} under Training Impact Assessment {2} ({3})"
				).format(self.evaluator_type, self.trainee_name, self.training_impact_assessment, existing)
			)

	def validate_assignment_membership(self):

		if not self.training_impact_assessment or not self.trainee_name:
			return

		assignment = frappe.db.get_value(
			"Training Impact Assessment Employee",
			{
				"parent": self.training_impact_assessment,
				"parenttype": "Training Impact Assessment",
				"employee": self.trainee_name,
			},
			["manager"],
			as_dict=True,
		)
		if not assignment:
			frappe.throw(
				_("Employee {0} is not assigned to Training Impact Assessment {1}").format(
					self.trainee_name, self.training_impact_assessment
				)
			)

		if self.evaluator_type == "Manager" and self.evaluator and assignment.manager:
			if self.evaluator != assignment.manager:
				frappe.throw(
					_("Evaluator must be {0}'s assigned Manager ({1}) for this Training Impact Assessment").format(
						self.trainee_name, assignment.manager
					)
				)

	def validate_evaluator(self):
		"""Sanity check: a Trainee response must be evaluated by the trainee themselves."""
		if self.evaluator_type == "Trainee" and self.evaluator and self.evaluator != self.trainee_name:
			frappe.throw(_("For a Trainee response, Evaluator must be the same as Trainee Name"))

	def validate_score_ranges(self):
		for row in self.assessment_criteria:
			for fieldname, label in (
				("before_training", _("Before Training")),
				("after_training", _("After Training")),
			):
				value = row.get(fieldname)
				if value in (None, ""):
					continue
				if value < 1 or value > 5:
					frappe.throw(_("Row #{0}: {1} score must be between 1 and 5").format(row.idx, label))

	def validate_after_training_timing(self):
		"""
		Business Rule: After Training results are recorded after Training Date.
		"""
		if not self.training_impact_assessment:
			return

		has_after_score = any(row.after_training not in (None, "") for row in self.assessment_criteria)
		if not has_after_score:
			return

		training_date = frappe.db.get_value(
			"Training Impact Assessment", self.training_impact_assessment, "training_date"
		)
		if training_date and getdate(nowdate()) < getdate(training_date):
			frappe.throw(
				_("After Training scores can only be recorded on or after the Training Date ({0})").format(
					frappe.format(training_date, {"fieldtype": "Date"})
				)
			)

	def validate_all_scores_present(self):
		"""Before allowing submission, make sure every criteria row has both scores."""
		for row in self.assessment_criteria:
			if row.before_training in (None, "") or row.after_training in (None, ""):
				frappe.throw(
					_("Row #{0}: Both Before Training and After Training scores are required before submitting").format(
						row.idx
					)
				)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_assigned_employees(doctype, txt, searchfield, start, page_len, filters):
	
	filters = filters or {}
	training_impact_assessment = filters.get("training_impact_assessment")
	column = filters.get("column") or "employee"

	if not training_impact_assessment or column not in ("employee", "manager"):
		return []

	return frappe.db.sql(
		"""
		select e.name, e.employee_name
		from `tabEmployee` e
		inner join `tabTraining Impact Assessment Employee` a
			on a.`{column}` = e.name and a.parenttype = 'Training Impact Assessment'
		where a.parent = %(parent)s
			and a.`{column}` is not null
			and a.`{column}` != ''
			and (e.name like %(txt)s or e.employee_name like %(txt)s)
		group by e.name
		order by
			case when e.name like %(txt)s then 0 else 1 end,
			e.name
		limit %(page_len)s offset %(start)s
		""".format(column=column),
		{
			"parent": training_impact_assessment,
			"txt": "%{}%".format(txt or ""),
			"start": start,
			"page_len": page_len,
		},
	)
def get_permission_query_conditions(user=None):
	
	user = user or frappe.session.user
	if user == "Administrator":
		return ""

	roles = frappe.get_roles(user)
	if "System Manager" in roles or "HR Manager" in roles or "HR User" in roles:
		return ""

	employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
	if not employee:
		return "1=0"

	return """(`tabTraining Assessment Response`.trainee_name = {employee}
		or `tabTraining Assessment Response`.evaluator = {employee})""".format(
		employee=frappe.db.escape(employee)
	)


def has_permission(doc, user=None, permission_type=None):
	user = user or frappe.session.user
	if user == "Administrator":
		return True

	roles = frappe.get_roles(user)
	if "System Manager" in roles or "HR Manager" in roles or "HR User" in roles:
		return True

	employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
	if not employee:
		return False

	return doc.trainee_name == employee or doc.evaluator == employee

