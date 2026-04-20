// Copyright (c) 2025, Guba Technology and contributors
// For license information, please see license.txt

frappe.query_reports["Sales VAT Report"] = {
	"filters": [
{
		"fieldname": "vat_category",
		"label": "VAT Category",
		"fieldtype": "Select",
		"options": "\ngoods\nservices"
},
{
		"fieldname":"month",
		"label": "Month",
		"fieldtype": "Select",
		"options": "\n 01 \n 02 \n 03 \n 04 \n 05 \n 06 \n 07 \n 08 \n 09 \n 10 \n 11 \n 12"
},
{
	"fieldname":"year",
	"label": "Fiscal Year",
	"fieldtype": "Link",
	"options": "Fiscal Year",

},
{
	"fieldname":"vat_date",
	"label": "VAT Date",
	"fieldtype": "Date",

},
			{
				"fieldname":"vat_type",
				"label": "VAT type",
				"fieldtype": "Select",
				"options":"\nVAT\nNon VAT\n7.5 percent"
			},
			{
				"fieldname":"from_date",
				"label": "From Date",
				"fieldtype": "Date",
			},
			{
				"fieldname":"to_date",
				"label": "To Date",
				"fieldtype": "Date",
			}

	]
};

