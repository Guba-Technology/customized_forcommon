// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Commitment", {
	refresh(frm) {

	},
    onload(frm) {
        today_year = frappe.datetime.get_today().split("-")[0];
        year = [];
        year.push("");
        for (let i =0; i < 100; i++) {
            year.push(today_year - i);
        }
        frm.set_value("year_taken", year);
        frm.set_df_property("year_taken", "options", year);
    }
});
