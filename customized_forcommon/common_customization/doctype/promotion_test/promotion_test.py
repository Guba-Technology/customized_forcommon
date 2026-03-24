# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class PromotionTest(Document):
	def validate(self):
		self.check_duplicates()
		self.make_document_submitted()
		self.check_result_not_more_than_100()
		self.calculate_and_set_ranks()

	def check_duplicates(self):
		if not self.employees_for_promotion_test:
			frappe.throw(
				_("Please add at least one employee for the promotion test before saving.")
			)
		else:
			employee_set = set()
			# Check for duplicate employees in the promotion test
			for row in self.employees_for_promotion_test:
				if row.employee in employee_set:
					frappe.throw(
						_("Employee {0} is already added for the promotion test.").format(row.employee)
					)
				employee_set.add(row.employee)
	
	def check_result_not_more_than_100(self):
		for row in self.employees_for_promotion_test:
			if row.result > 100:
				frappe.throw(
					_("Result for employee {0} cannot be more than 100.").format(row.employee)
				)
	def calculate_and_set_ranks(self):
		# 1. Clear existing ranks in the 'Promotion Test Rank' table
		self.set("promotion_test_rank", []) # Clears all rows

		if not self.employees_for_promotion_test:
			frappe.msgprint("No employees found for promotion test to calculate ranks.", alert=True)
			return

		# 2. Get employees and their results
		employee_results = []
		for row in self.employees_for_promotion_test:
			employee_results.append({
				"employee": row.employee,
				"employee_name": row.employee_name, # Include name for convenience
				"result": row.result
			})

		# 3. Sort employees by result in descending order
		sorted_employees = sorted(employee_results, key=lambda x: x['result'], reverse=True)

		# 4. Calculate and assign ranks, handling ties
		current_rank = 1
		previous_result = None
		for i, emp_data in enumerate(sorted_employees):
			# If this is not the first employee AND their result is different from the previous one,
			# then update the rank. Otherwise, they share the same rank as the previous.
			if i > 0 and emp_data['result'] != previous_result:
				current_rank += 1

			# Add a new row to the 'Promotion Test Rank' child table
			self.append("promotion_test_rank", {
				"employee": emp_data['employee'],
				"name1": emp_data['employee_name'], # Use name1 as per your DocType
				"result": emp_data['result'],
				"rank": current_rank
			})
			previous_result = emp_data['result'] # Update previous_result for the next iteration

		
		frappe.msgprint("Promotion Test Ranks calculated successfully!", alert=True)

	def make_document_submitted(self):
		if self.status == "Finished":
			self.docstatus = 1
			frappe.msgprint(_("Promotion Test has been Finished."), alert=True)

	def before_cancel(self):
		if self.status == "Finished":
			frappe.throw(_("Cannot cancel a Promotion Test that has already been finished."))

	
