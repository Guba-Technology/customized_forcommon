# Copyright (c) 2025, Guba Technology and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import now
import datetime
from customized_forcommon.custom_report.my_utilities.get_company_info import GetCompanyInfo
from customized_forcommon.custom_report.my_utilities.get_last_day import GetLastDay
get_company_info = GetCompanyInfo()

def execute(filters=None):
	filters = filters or {}
	conditions = {}
	filter_data = ["name", "custom_employee_tin", "employee_name", "custom_pid",  "ctc"]
	for ff in filter_data:
		if filters.get(ff):
			conditions[ff] = ["like", f"%{filters.get(ff)}%"]
	def get_date_condition(field_name, date_value, is_range):
		if not date_value:
			return None
		if is_range:
			return  (">=", date_value) 
		return ("=", date_value)

	for field in ["date_of_joining", "relieving_date"]:
		condition = get_date_condition(field, filters.get(field), filters.get("is_range"))
		if condition:
			conditions[field] = condition
	
	


	columns = [
		{"label": "Employee", "fieldname": "name", "fieldtype": "Link", "options": "Employee", "width": 200},
		{"label": "Employee TIN", "fieldname": "custom_employee_tin", "fieldtype": "data", },
		{"label": "Full Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
		{"label": "Pension ID", "fieldname": "custom_pid", "fieldtype": "data"},
		{"label": "Start Date", "fieldname": "date_of_joining","fieldtype": "date"},
		{"label": "end_date", "fieldname": "relieving_date", "fieldtype": "date"},
		{"label": "Basic Salary", "fieldname": "ctc", "fieldtype": "float"},
		
		
	]
	data = []
	pension_payable_account = get_company_info.get_pension_payable_account()
	pension_receivable_account = get_company_info.get_pension_receivable_account()
	if pension_payable_account or pension_receivable_account:

		employee = frappe.get_all(
			"Employee",
			fields=["name", "custom_employee_tin", "employee_name","middle_name", "last_name", "custom_pid", "date_of_joining", "relieving_date", "ctc"],
			filters=conditions,
		)
		for emp in employee:
			
			data.append({
					"name": emp.name,
					"custom_employee_tin": emp.custom_employee_tin,
					"employee_name": emp.employee_name,
					"custom_pid": emp.custom_pid,
					"date_of_joining": emp.date_of_joining,
					"relieving_date": emp.relieving_date,
					"ctc":emp.ctc ,
				})	
		return columns, data
	else:
		frappe.throw(
			"Pension payable account or pension receivable account not found. Please set in <a href='/app/company/{0}'>{0}</a> <br> available at <b>VAT Account </b> tab".format(
				get_company_info.Company
			)
		)
		
