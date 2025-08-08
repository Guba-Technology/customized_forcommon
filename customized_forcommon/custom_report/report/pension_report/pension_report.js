// Copyright (c) 2025, Guba Technology and contributors
// For license information, please see license.txt

frappe.query_reports["pension report"] = {
	"filters": [
		{
			"fieldname": "name",
			"label": "Employee",
			"fieldtype": "Link",
			"options": "Employee",
		},
		{
			"fieldname": "custom_employee_tin",
			"label": "Employee TIN",
			"fieldtype": "Data",
			
		},
		{
			"fieldname": "employee_name",
			"label": "Full Name",
			"fieldtype": "Data",
		},
		{
			"fieldname": "custom_pid",
			"label": "Pension ID",
			"fieldtype": "Data",
		},
		{
			"fieldname":"date_of_joining",
			"label": "Start Date",
			"fieldtype": "Date",
		},
		{
			"fieldname":"relieving_date",
			"label": "End Date",
			"fieldtype": "Date",
		}
		,
		{
			"fieldname":"is_range",
			"label": "Use Date Range",
			"fieldtype": "Check"
		},
		{
			"fieldname": "ctc",
			"label": "Basic Salary",
			"fieldtype": "Data",
			
		}
	]
};
