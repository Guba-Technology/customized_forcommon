# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate

class Clearance(Document):
	def validate(self):
		self.check_existing_clearance()
		self.change_status_to_approved()
		self.fetching_approver_details()
		self.set_employee_status_to_left()

	def check_existing_clearance(self):
		employee = frappe.get_all(
			"Clearance",
			filters={
				"employee": self.employee,
				# "docstatus": 1, 
				"name": ["!=", self.name],
				"status": "Approved"
			}
		)
		if employee:
			frappe.throw(
				_("An approved clearance already exists for this employee: {0}").format(self.employee)
			)

	def change_status_to_approved(self):
		if self.clearance_table:
			all_approved = True
			for row in self.clearance_table:
				if row.status != 'Approved':
					all_approved = False
					break

			if all_approved:
				self.status = 'Approved'
				self.docstatus = 1  # Set the document status to 'Submitted'
				frappe.msgprint("All clearance items are approved. Clearance status is Updated to 'Approved'.")
			else:
				self.status = 'Pending'
		else:
			frappe.throw(_("Clearance table cannot be empty."))
	
	# Fetching approver details when status changes from Pending to Approved
	def fetching_approver_details(self):
		""" Fetching approver details when status changes from Pending to Approved
		or from Approved to Pending
		1. If status changes from Pending to Approved, set approver details
		2. If status changes from Approved to Pending, check if the current user is the original approver
		3. If not, throw an error
		"""
		current_user = frappe.session.user
		employee = frappe.get_value("Employee", {"user_id": current_user}, "name")
		employee_name = frappe.get_value("Employee", employee, "employee_name")

		if not employee:
			frappe.throw("Your user is not linked to any Employee record.")

		prev_doc = self.get_doc_before_save()

		for idx, row in enumerate(self.clearance_table):
			prev_status = None
			if prev_doc and len(prev_doc.clearance_table) > idx:
				prev_status = prev_doc.clearance_table[idx].status
			# Status changed from Pending → Approved
			if prev_status == "Pending" and row.status == "Approved":
				row.approver = employee
				row.approver_name = employee_name
				row.approver_salutation = frappe.get_value("Employee", employee, "salutation")
				row.approver_responsibility = frappe.get_value("Employee", employee, "designation")
				row.date = nowdate()
				if not row.approver_name:
					frappe.throw(
						_("Approver name is required when status is changed to Approved.")
					)
				if not row.approver_responsibility:
					frappe.throw(
						_("Approver responsibility/designation is required when status is changed to Approved.")
					)
			# Status changed from Approved → Pending
			elif prev_status == "Approved" and row.status == "Pending":
				if row.approver_name != employee_name:
					frappe.throw(
						f"Only the original approver ({row.approver_name}) can revert this status."
					)

	def set_employee_status_to_left(self):
		if self.status == "Approved":
			employee = frappe.get_doc("Employee", self.employee)
			if employee.status != "Left":
				employee.status = "Left"
				employee.relieving_date = nowdate()  # Set the relieving date to today
				employee.save()

				link = ", ".join([
					f'<a href="/app/employee/{employee.name}">{employee.name}</a>'
				])
				frappe.msgprint(_(f"{link} status has been updated to 'Left'."))

