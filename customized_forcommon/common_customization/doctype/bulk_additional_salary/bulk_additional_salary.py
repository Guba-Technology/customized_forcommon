# Copyright (c) 2026, Guba Technology and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BulkAdditionalSalary(Document):
	def validate(self):
		if not self.employees:
			frappe.throw("No Employees found")
		self.validate_amount()
		self.set_amount()

	def validate_amount(self):
		currency = frappe.db.get_value("Company", self.company, "default_currency")
		if self.salary_type == "Common":
			if self.amount <= 0:
				frappe.throw(f"Amount must be greater than 0 {currency}")

	def set_amount(self):
		if not self.employees:
			return

		if self.salary_type == "Common" and self.amount:
			for emp in self.employees:
				emp.amount = self.amount

		elif self.salary_type == "Based on CTC" and self.rate:
			for emp in self.employees:
				ctc = frappe.db.get_value("Employee", emp.employee, "ctc") or 0
				emp.amount = ctc * self.rate / 100

	def on_submit(self):
		if not self.employees:
			frappe.throw("No Employees found")
		currency = frappe.db.get_value("Company", self.company, "default_currency")
		for emp in self.employees:
			additional_salary = frappe.new_doc("Additional Salary")
			additional_salary.employee = emp.employee
			additional_salary.salary_component = self.salary_component
			additional_salary.payroll_date = self.payroll_date
			additional_salary.company = self.company
			additional_salary.currency = currency
			additional_salary.amount = emp.amount
			additional_salary.ref_doctype = self.doctype
			additional_salary.ref_docname = self.name
			additional_salary.overwrite_salary_structure_amount = 0

			additional_salary.insert(ignore_permissions=True)
			additional_salary.submit()

	def on_cancel(self):
		additional_salaries = frappe.get_all(
			"Additional Salary",
			filters={
				"ref_doctype": self.doctype,
				"ref_docname": self.name
			},
			fields=["name"]
		)

		for sal in additional_salaries:
			doc = frappe.get_doc("Additional Salary", sal.name)
			if doc.docstatus == 1:
				doc.cancel()

@frappe.whitelist()
def get_filtered_employees(company=None, filtered_by=None, value=None):

    filters = {
        "company": company,
        "status": "Active"
    }

    # Mapping filter field
    field_map = {
        "Gender": "gender",
        "Employee Grade": "grade",
        "Designation": "designation",
        "Department": "department",
        "Employee Group": "employee_group",
        "Branch": "branch",
        "Employment Type": "employment_type"
    }

    if filtered_by and filtered_by != "All" and value:
        filters[field_map.get(filtered_by)] = value

    employees = frappe.get_all(
        "Employee",
        filters=filters,
        fields=["name", "employee_name"],
		order_by="creation asc"
    )

    return employees