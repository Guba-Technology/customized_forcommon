// Copyright (c) 2026, Guba Technology and contributors
// For license information, please see license.txt

frappe.query_reports["Training Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 0
		},
		{
			"fieldname": "training_plan",
			"label": __("Training Plan"),
			"fieldtype": "Link",
			"options": "Training Plan"
		},
		{
			"fieldname": "training_program",
			"label": __("Training Program"),
			"fieldtype": "Link",
			"options": "Training Program"
		},
		{
			"fieldname": "training_event",
			"label": __("Training Event"),
			"fieldtype": "Link",
			"options": "Training Event"
		},
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		}
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
        
		// Make specific statuses bold or colored for better analysis
		if (column.fieldname == "event_status" && data && data.event_status == "Completed") {
			value = "<span style='color:green; font-weight:bold'>" + value + "</span>";
		}
		if (column.fieldname == "event_status" && data && data.event_status == "Cancelled") {
			value = "<span style='color:red; font-weight:bold'>" + value + "</span>";
		}

		return value;
	},
    "tree": true, // Enables the collapsible indented view natively
    "name_field": "training_plan", // Defines the root level of the tree
    "parent_field": "parent"
};