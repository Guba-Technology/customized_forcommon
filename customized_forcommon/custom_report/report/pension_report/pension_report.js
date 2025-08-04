// Copyright (c) 2025, Guba Technology and contributors
// For license information, please see license.txt

frappe.query_reports["pension report"] = {
	"filters": [
		{
			"fieldname": "custom_employee_tin",
			"label": "Employee TIN",
			"fieldtype": "Data",
			
		},
		{
			"fieldname": "full_name",
			"label": "Full Name",
			"fieldtype": "Data",
		},
		{
			"fieldname": "custom_pid",
			"label": "Pension ID",
			"fieldtype": "Data",
		},
		{
			"field type":"start_date",
			"label": "Start Date",
			"fieldtype": "Date",
		},
		{
			"field type":"end_date",
			"label": "End Date",
			"fieldtype": "Date",
		},
		{
			"fieldname": "basic_salary",
			"label": "Basic Salary",
			"fieldtype": "float",
			
		}
	]
};
