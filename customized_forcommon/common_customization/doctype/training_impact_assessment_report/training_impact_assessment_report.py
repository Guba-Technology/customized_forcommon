# Copyright (c) 2026, Guba Technology
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class TrainingImpactAssessmentReport(Document):
	pass


def _average(values):
	values = [v for v in values if v not in (None, "")]
	if not values:
		return None
	return sum(values) / len(values)


def generate_report(training_impact_assessment):
	"""
	Consolidate all SUBMITTED Training Assessment Response records for the given
	Training Impact Assessment into a single Training Impact Assessment Report,
	per the Business Rules:
	  - results are calculated per Training Impact Assessment (not per employee)
	  - only submitted trainee/manager responses are used
	  - the report is created if missing, or updated in place if it already exists
	"""
	if not training_impact_assessment:
		return

	tia = frappe.get_doc("Training Impact Assessment", training_impact_assessment)

	# Criteria order comes from the Assessment Template so the report layout is stable
	# even if responses were created/edited in a different order.
	criteria_order = []
	if tia.assessment_template:
		template = frappe.get_doc("Training Assessment Template", tia.assessment_template)
		criteria_order = [row.criteria for row in template.criteria]

	responses = frappe.get_all(
		"Training Assessment Response",
		filters={"training_impact_assessment": training_impact_assessment, "docstatus": 1},
		fields=["name", "evaluator_type"],
	)

	# collected[criteria_text] = {"trainee_before": [...], "trainee_after": [...],
	#                              "manager_before": [...], "manager_after": [...]}
	collected = {}
	for c in criteria_order:
		collected[c] = {"trainee_before": [], "trainee_after": [], "manager_before": [], "manager_after": []}

	for resp in responses:
		evaluator_type = resp.evaluator_type  # "Trainee" or "Manager"
		rows = frappe.get_all(
			"Training Assessment Response Criteria",
			filters={"parent": resp.name, "parenttype": "Training Assessment Response"},
			fields=["criteria", "before_training", "after_training"],
			order_by="idx",
		)
		for row in rows:
			key = row.criteria
			if key not in collected:
				# Response used criteria text not (or no longer) present in the template;
				# still capture it so no data is silently dropped from the report.
				collected[key] = {
					"trainee_before": [],
					"trainee_after": [],
					"manager_before": [],
					"manager_after": [],
				}
				criteria_order.append(key)

			bucket = "trainee" if evaluator_type == "Trainee" else "manager"
			if row.before_training not in (None, ""):
				collected[key][f"{bucket}_before"].append(row.before_training)
			if row.after_training not in (None, ""):
				collected[key][f"{bucket}_after"].append(row.after_training)

	result_rows = []
	overall_averages = {"trainee_before": [], "trainee_after": [], "manager_before": [], "manager_after": []}

	for criteria in criteria_order:
		data = collected[criteria]

		trainee_before = _average(data["trainee_before"])
		trainee_after = _average(data["trainee_after"])
		manager_before = _average(data["manager_before"])
		manager_after = _average(data["manager_after"])

		average_before = _average([v for v in (trainee_before, manager_before) if v is not None])
		average_after = _average([v for v in (trainee_after, manager_after) if v is not None])
		difference = (
			(average_after - average_before) if (average_after is not None and average_before is not None) else None
		)

		result_rows.append(
			{
				"criteria": criteria,
				"trainee_before": trainee_before,
				"trainee_after": trainee_after,
				"manager_before": manager_before,
				"manager_after": manager_after,
				"average_before": average_before,
				"average_after": average_after,
				"difference": difference,
			}
		)

		if trainee_before is not None:
			overall_averages["trainee_before"].append(trainee_before)
		if trainee_after is not None:
			overall_averages["trainee_after"].append(trainee_after)
		if manager_before is not None:
			overall_averages["manager_before"].append(manager_before)
		if manager_after is not None:
			overall_averages["manager_after"].append(manager_after)

	# Trailing "Overall Average" row, mirroring the aggregate row in the source template.
	if result_rows:
		o_trainee_before = _average(overall_averages["trainee_before"])
		o_trainee_after = _average(overall_averages["trainee_after"])
		o_manager_before = _average(overall_averages["manager_before"])
		o_manager_after = _average(overall_averages["manager_after"])
		o_average_before = _average([v for v in (o_trainee_before, o_manager_before) if v is not None])
		o_average_after = _average([v for v in (o_trainee_after, o_manager_after) if v is not None])
		o_difference = (
			(o_average_after - o_average_before)
			if (o_average_after is not None and o_average_before is not None)
			else None
		)

		result_rows.append(
			{
				"criteria": _("Overall Average"),
				"trainee_before": o_trainee_before,
				"trainee_after": o_trainee_after,
				"manager_before": o_manager_before,
				"manager_after": o_manager_after,
				"average_before": o_average_before,
				"average_after": o_average_after,
				"difference": o_difference,
			}
		)

	if frappe.db.exists("Training Impact Assessment Report", training_impact_assessment):
		report = frappe.get_doc("Training Impact Assessment Report", training_impact_assessment)
	else:
		report = frappe.new_doc("Training Impact Assessment Report")
		report.training_impact_assessment = training_impact_assessment

	report.set("results", [])
	for row in result_rows:
		report.append("results", row)
	report.last_generated_on = now_datetime()

	if report.is_new():
		report.insert(ignore_permissions=True)
	else:
		report.save(ignore_permissions=True)

	return report.name
