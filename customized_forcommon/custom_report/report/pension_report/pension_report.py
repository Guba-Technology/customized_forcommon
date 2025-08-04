# Copyright (c) 2025, Guba Technology and contributors
# For license information, please see license.txt


import frappe

def execute(filters=None):
	filters = filters or {}
	conditions = {}
	if filters.get("employee PIN"):
		conditions["custom_employee_pin"] = filters["employee PIN"] 
	if filters.get("employe name"):
		conditions["employee_name"] = filters["employe name"]

	if filters.get("PID"):
		conditions["custom_pid"] = filters["PID"]
	if filters.get("start date"):
		conditions["start_date"] = filters["start date"]
	if filters.get("end date"):
		conditions["end_date"] = filters["end date"]
	if filters.get("basic salary"):
		conditions["basic_salary"] = filters["basic salary"]
	


	columns = [
		{"label": "Employee TIN", "fieldname": "custom_employee_tin", "fieldtype": "data", },
		{"label": "Full Name", "fieldname": "full_name", "fieldtype": "Link", "options": "Employee"},
		{"label": "Pension ID", "fieldname": "custom_pid", "fieldtype": "data"},
		{"label": "Start Date", "fieldname": "start_date","fieldtype": "date"},
		{"label": "end_date", "fieldname": "end_date", "fieldtype": "date"},
		{"label": "Basic Salary", "fieldname": "basic_salary", "fieldtype": "float"},
		
		
	]
	data = []

	employee = frappe.get_all(
		"Employee",
		fields=["name"],
		filters=conditions,
	)
	for emp in employee:
		full_name = emp.first_name +" " + emp.middle_name + " " + emp.last_name
		data.append({
				"custom_employee_tin": emp.custom_employee_tin,
				"full_name": full_name,
				"custom_pid": emp.custom_pid,
				"start_date": emp.start_date,
				"end_date": emp.end_date,
				"basic_salary":emp.basic_salary ,
				
				
			})
	
	
	
	
		
	return columns, data
