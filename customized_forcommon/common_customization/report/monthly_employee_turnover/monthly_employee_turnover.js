// Copyright (c) 2026, Guba Technology and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Employee Turnover"] = {
	filters: [
		{
			fieldname: "fiscal_year",
			label: "Fiscal Year",
			fieldtype: "Link",
			options: "Fiscal Year",
			default: frappe.defaults.get_user_default("fiscal_year")
		}
	]
};