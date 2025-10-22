# Copyright (c) 2025, Guba Technology and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TrainingReport(Document):
	def validate(self):
		try:
			employee = self.get("employee")
			print("self training event ", self.get("training_event"))
			if employee not in get_employee_list(self.get("training_event")):
				frappe.throw("This Employee is not present in the training event")
		except:
			frappe.msgprint("please select the training event first")

	pass
@frappe.whitelist()
def get_employee_list(training_event):
	if training_event is None:
		return
	training_event_emp = frappe.get_all("Training Event Employee", fields=["employee","attendance"], filters = {"attendance":"Present", "parent": training_event}, distinct=True)
	return [emp["employee"] for emp in training_event_emp]
