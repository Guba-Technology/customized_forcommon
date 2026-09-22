# Copyright (c) 2026, Guba Technology
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class TrainingImpactAssessmentReport(Document):
	pass


def _calculate_cs(values):
	values = [float(v) for v in values if v not in (None, "")]
	if not values:
		return None
	
	te = len(values)
	ms = 5
	
	if te == 0 or ms == 0:
		return 0.0
		
	return sum(values) / (te * ms) * 100


def _calculate_combined_average(score1, score2):
	if score1 is None and score2 is None:
		return None
	
	s1 = score1 if score1 is not None else 0.0
	s2 = score2 if score2 is not None else 0.0
	
	return (s1 + s2) / 2.0


def generate_report(training_impact_assessment):
	if not training_impact_assessment:
		return

	tia = frappe.get_doc("Training Impact Assessment", training_impact_assessment)

	criteria_order = []
	if tia.assessment_template:
		template = frappe.get_doc("Training Assessment Template", tia.assessment_template)
		criteria_order = [row.criteria for row in template.criteria]

	responses = frappe.get_all(
		"Training Assessment Response",
		filters={"training_impact_assessment": training_impact_assessment, "docstatus": 1},
		fields=["name", "evaluator_type"],
	)

	collected = {}
	for c in criteria_order:
		collected[c] = {"trainee_before": [], "trainee_after": [], "manager_before": [], "manager_after": []}

	for resp in responses:
		evaluator_type = resp.evaluator_type
		rows = frappe.get_all(
			"Training Assessment Response Criteria",
			filters={"parent": resp.name, "parenttype": "Training Assessment Response"},
			fields=["criteria", "before_training", "after_training"],
			order_by="idx",
		)
		
		for row in rows:
			key = row.criteria
			if key not in collected:
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

	for criteria in criteria_order:
		data = collected[criteria]
		
		trainee_before = _calculate_cs(data["trainee_before"])
		trainee_after = _calculate_cs(data["trainee_after"])
		manager_before = _calculate_cs(data["manager_before"])
		manager_after = _calculate_cs(data["manager_after"])

		avg_before = _calculate_combined_average(trainee_before, manager_before)
		avg_after = _calculate_combined_average(trainee_after, manager_after)
		
		diff = (avg_after - avg_before) if (avg_after is not None and avg_before is not None) else None
		
		result_rows.append(
			{
				"criteria": criteria,
				"trainee_before": trainee_before,
				"trainee_after": trainee_after,
				"manager_before": manager_before,
				"manager_after": manager_after,
				"average_before": avg_before,
				"average_after": avg_after,
				"difference": diff,
			}
		)

	if result_rows:
		t_befores = [r["trainee_before"] for r in result_rows if r["trainee_before"] is not None]
		t_afters = [r["trainee_after"] for r in result_rows if r["trainee_after"] is not None]
		m_befores = [r["manager_before"] for r in result_rows if r["manager_before"] is not None]
		m_afters = [r["manager_after"] for r in result_rows if r["manager_after"] is not None]
		
		o_trainee_before = sum(t_befores) / len(t_befores) if t_befores else 0.0
		o_trainee_after = sum(t_afters) / len(t_afters) if t_afters else 0.0
		o_manager_before = sum(m_befores) / len(m_befores) if m_befores else 0.0
		o_manager_after = sum(m_afters) / len(m_afters) if m_afters else 0.0
		
		o_average_before = (o_trainee_before + o_manager_before) / 2.0
		o_average_after = (o_trainee_after + o_manager_after) / 2.0
		o_difference = o_average_after - o_average_before

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
