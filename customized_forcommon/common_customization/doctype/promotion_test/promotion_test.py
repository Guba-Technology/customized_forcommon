# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class PromotionTest(Document):
	def validate(self):
		self.check_duplicates()
		self.check_result_not_more_than_weight()
		self.validate_total_weight_per_employee()
		self.make_document_submitted()
		self.calculate_and_set_ranks()

	def check_duplicates(self):
		if not self.employees_for_promotion_test:
			frappe.throw(
				_("Please add at least one employee for the promotion test before saving.")
			)

		seen = set()

		for row in self.employees_for_promotion_test:
			if not row.employee or not row.criteria:
				frappe.throw(_("Employee and Criteria are required in all rows."))

			key = (row.employee, row.criteria)

			if key in seen:
				frappe.throw(
					_("Duplicate entry found: Employee {0} with Criteria {1} already exists.")
					.format(row.employee, row.criteria)
				)

			seen.add(key)
	
	def check_result_not_more_than_weight(self):
		for row in self.employees_for_promotion_test:
			if not row.criteria:
				frappe.throw(_("Please select Criteria for employee {0}.").format(row.employee))

			weight = frappe.db.get_value("Promotion Test Criteria", row.criteria, "weight") or 0

			if row.result > weight:
				frappe.throw(
					_("Result for employee {0} under Criteria {1} cannot exceed weight ({2}).")
					.format(row.employee, row.criteria, weight)
				)
	def validate_total_weight_per_employee(self):
		# Group rows by employee
		employee_criteria_map = {}

		for row in self.employees_for_promotion_test:
			if not row.employee or not row.criteria:
				frappe.throw(_("Employee and Criteria are required in all rows."))

			employee_criteria_map.setdefault(row.employee, set()).add(row.criteria)

		# Fetch all needed weights once
		all_criteria = list({
			row.criteria for row in self.employees_for_promotion_test if row.criteria
		})

		criteria_weights = frappe.get_all(
			"Promotion Test Criteria",
			filters={"name": ["in", all_criteria]},
			fields=["name", "weight"]
		)

		weight_map = {d.name: d.weight for d in criteria_weights}

		# Validate per employee
		for employee, criteria_set in employee_criteria_map.items():
			total_weight = sum(weight_map.get(c, 0) for c in criteria_set)

			if total_weight != 100:
				frappe.throw(
					_("Total criteria weight for employee {0} must be exactly 100. Current total is {1}.")
					.format(employee, total_weight)
				)
	def calculate_and_set_ranks(self):
		# 1. Clear existing ranks
		self.set("promotion_test_rank", [])

		if not self.employees_for_promotion_test:
			frappe.msgprint("No employees found for promotion test to calculate ranks.", alert=True)
			return

		# 2. Aggregate total result per employee
		employee_totals = {}

		for row in self.employees_for_promotion_test:
			if not row.employee:
				continue

			if row.employee not in employee_totals:
				employee_totals[row.employee] = {
					"employee_name": row.employee_name,
					"total": 0
				}

			# sum up the result
			employee_totals[row.employee]["total"] += row.result

		# 3. Convert to list
		employee_results = [
			{
				"employee": emp,
				"employee_name": data["employee_name"],
				"result": data["total"]
			}
			for emp, data in employee_totals.items()
		]

		# 4. Sort descending
		sorted_employees = sorted(employee_results, key=lambda x: x["result"], reverse=True)

		# 5. Assign ranks (competition ranking: 1,1,3)
		current_rank = 1
		previous_result = None

		for i, emp_data in enumerate(sorted_employees):
			if i > 0 and emp_data["result"] != previous_result:
				current_rank += 1 

			self.append("promotion_test_rank", {
				"employee": emp_data["employee"],
				"name1": emp_data["employee_name"],
				"result": emp_data["result"],
				"rank": current_rank
			})

			previous_result = emp_data["result"]

		frappe.msgprint("Promotion Test Ranks calculated successfully!", alert=True)

	def make_document_submitted(self):
		if self.status == "Finished":
			self.docstatus = 1
			frappe.msgprint(_("Promotion Test has been Finished."), alert=True)

	def before_cancel(self):
		if self.status == "Finished":
			frappe.throw(_("Cannot cancel a Promotion Test that has already been finished."))


	