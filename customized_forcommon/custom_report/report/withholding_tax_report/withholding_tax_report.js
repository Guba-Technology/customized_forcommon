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
	"fieldtype": "Select",
	"options": (() => {
		let options = [];
		let currentYear = (new Date()).getFullYear();
		for (let i = 0; i <= 20; i++) {
			options.push((currentYear - i).toString());
		}
		return options.join("\n");
	})()
}
    ]
};
