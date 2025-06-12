# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class MaintenanceRequest(Document):
	def validate(self):
		self.validate_duplicate_maintenance_department()
		self.validate_duplicate_employee()
		self.validate_dulicate_material_type()

	def validate_duplicate_maintenance_department(self):
		departments = set()
		if self.maintenance_department:
			for department in self.maintenance_department:
				if department.maintenance_department in departments:
					frappe.throw(
						_("Duplicate Maintenance Department: {0}").format(department.maintenance_department))
				departments.add(department.maintenance_department)

	def validate_duplicate_employee(self):
		employees = set()
		if self.employee_name:
			for emp in self.employee_name:
				if emp.employee in employees:
					frappe.throw(_("Duplicate Employee: {0}").format(emp.employee))
				employees.add(emp.employee)
	
		# # Check if the number of employees exceeds the limit
		# # Assuming the maximum allowed employees is 3
		# if len(employees) > 3:
		# 	frappe.throw(_("You can only select a maximum of 3 employees for a maintenance request."))


	def validate_dulicate_material_type(self):
		materials = set()
		if self.material_type:
			for material in self.material_type:
				if material.maintenance_material in materials:
					frappe.throw(_("Duplicate Material Type: {0}").format(material.maintenance_material))
				materials.add(material.maintenance_material)
