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
	],
	get_datatable_options(options) {
		options.serialNoColumn = false;  // 🔥 disable default index column
		return options;
	},
	formatter: function (value, row, column, data, default_formatter) {

		value = default_formatter(value, row, column, data);

		if (data && data.beginning === "Annual") {
			return `<span style="font-weight:700;">${value}</span>`;
		}

		return value;
	}
};