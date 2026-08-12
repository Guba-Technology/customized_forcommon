// Copyright (c) 2026, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("Salary Payment Distribution Request", {
    setup(frm) {
        frm.set_query("employee", () => {
            return {
                filters: {
                    company: frm.doc.company,
                    status: "Active"
                }
            };
        });
    },
    refresh(frm) {

    },
});
