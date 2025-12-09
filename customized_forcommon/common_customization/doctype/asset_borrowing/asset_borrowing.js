// Copyright (c) 2025, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("Asset Borrowing", {
	refresh(frm) {
         if (frm.doc.status === "Borrowed") {
            frm.page.set_indicator('Borrowed', 'orange');
        }else if(frm.doc.status === "Returned"){
            frm.page.set_indicator('Returned', 'red');
        }
        frm.set_query("asset", () => {
    return {
        filters: [
            ["Asset", "docstatus", "=", 1],
            ["Asset", "status", "not in", ["Borrowed", "Scrapped", "Sold"]]
        ]
    };
});


	},
});
