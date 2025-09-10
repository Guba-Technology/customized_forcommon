// Copyright (c) 2025, Guba Technology and contributors
// For license information, please see license.txt

frappe.query_reports["Withholding Tax Report"] = {
    filters: [
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
	"fieldname":"withholding_date",
	"label": "Withholding Date",
	"fieldtype": "Date",

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
			,
			{
				"fieldname":"filter_type",
				"label": "Filter Type",
				"fieldtype": "Select",
				"options": "\nSales Invoice\nPurchase Invoice"
			}
    ]
};
