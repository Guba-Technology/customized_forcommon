# Copyright (c) 2026, Guba Technology and Contributors
# See license.txt

import frappe
import json
from frappe import _
from frappe.model.document import Document

class TestTrainingImpactAssessment(Document):
	pass


@frappe.whitelist()
def get_filtered_employees(filters=None):
	if isinstance(filters, str):
		filters = json.loads(filters)
	filters = frappe._dict(filters or {})

	employee_filters = {"status": "Active"}

	# Handle basic exact-match filters
	for fieldname in ("company", "designation", "branch", "grade", "department"):
		if filters.get(fieldname):
			employee_filters[fieldname] = filters.get(fieldname)

	
	if filters.get("shift"):
		employee_filters["default_shift"] = filters.get("shift")

	return frappe.get_all(
		"Employee",
		filters=employee_filters,
		fields=[
			"name as employee",
			"employee_name",
			"department",
			"designation",
			"reports_to as manager",
		],
		order_by="employee_name",
	)