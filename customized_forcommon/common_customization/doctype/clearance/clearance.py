# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate

class Clearance(Document):
	def validate(self):
		self.check_existing_clearance()
		self.check_active_warranty_request()
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
				"status": "Approved",
				"docstatus": 1  # Ensure we only check for submitted documents
			}
		)
		if employee:
			frappe.throw(
				_("An approved clearance already exists for this employee: {0}").format(self.employee)
			)
	# Check if there is an active warranty request for the employee
	def check_active_warranty_request(self):
		"""Check if there is an active warranty request for the employee."""
		active_warranty = frappe.get_all(
			"Warranty Request",
			filters={
				"employee": self.employee,
				"status": "Active"
			}
		)
		if active_warranty:
			link = ", ".join([
				f'<a href="/app/warranty-request/{warranty.name}">{warranty.name}</a>'
				for warranty in active_warranty
			])
			frappe.throw(
				_("There is an active warranty request for this employee: {0}").format(link)
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
				frappe.msgprint("All clearance items are approved. Clearance status is Updated to 'Approved'.")
				self.docstatus = 1  # Set the document status to 'Submitted'
			else:
				self.status = 'Pending'
		else:
			frappe.throw(_("Clearance table cannot be empty."))
	
	# Fetching approver details when status changes from Pending to Approved
	def fetching_approver_details(self):
		current_user = frappe.session.user
		employee = frappe.get_value("Employee", {"user_id": current_user}, "name")
		employee_name = frappe.get_value("Employee", employee, "employee_name")

		if not employee:
			frappe.throw("Your user is not linked to any Employee record.")

		prev_doc = self.get_doc_before_save()
		prev_rows = {row.department: row for row in prev_doc.clearance_table} if prev_doc else {}

		for row in self.clearance_table:
			prev_status = prev_rows.get(row.department).status if prev_rows.get(row.department) else None
			prev_approver_name = prev_rows.get(row.department).approver_name if prev_rows.get(row.department) else None

			# 1. New row or changed to Approved
			if (not prev_status and row.status == "Approved") or (prev_status == "Pending" and row.status == "Approved"):
				row.approver = employee
				row.approver_name = employee_name
				row.approver_salutation = frappe.get_value("Employee", employee, "salutation")
				row.approver_responsibility = frappe.get_value("Employee", employee, "designation")
				row.date = nowdate()

				# Required fields check
				missing_fields = []
				if not row.approver_name:
					missing_fields.append("Approver Name")
				if not row.approver_responsibility:
					missing_fields.append("Approver Responsibility")
				if not row.date:
					missing_fields.append("Date")

				if missing_fields:
					link = ", ".join([
						f'<a href="/app/employee/{employee}">{employee_name}</a>'
					])
					if len(missing_fields) == 1 and missing_fields[0] == "Approver Responsibility":
						frappe.throw(_("The Employee designation is required for the employee {0} linked with the current user when approving a row.").format(link))
					elif len(missing_fields) == 1:
						frappe.throw(_("The following field is required for the employee {0} linked with the current user when approving a row: {1}").format(link, missing_fields[0]))
					else:
						frappe.throw(
							_("The following fields are required for the employee {0} linked with the current user when approving a row: {1}").format(link, ", ".join(missing_fields))
						)

			# 2. Approved → Pending
			elif prev_status == "Approved" and row.status == "Pending":
				if prev_approver_name != employee_name:
					frappe.throw(
						f"Only the original approver ({prev_approver_name or 'Unknown'}) can revert this status."
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

	def before_cancel(self):
		if self.status == "Approved":
			frappe.throw(_("Can't cancel approved clearance"))

