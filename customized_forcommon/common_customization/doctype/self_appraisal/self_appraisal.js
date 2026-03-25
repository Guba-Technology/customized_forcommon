// Copyright (c) 2026, guba and contributors
// For license information, please see license.txt

frappe.ui.form.on("Self Appraisal", {
    setup(frm) {
        frm.set_query("employee", () => ({
            filters: { status: "Active" }
        }));

        frm.set_query("appraisal", () => ({
            filters: {
                employee: frm.doc.employee,
                docstatus: 0
            }
        }));
    },
    employee(frm) {
        frm.set_value("appraisal", null)
        // Clear existing rows
        frm.set_value("appraisal_template");
    },
   appraisal_template(frm) {
		if (frm.doc.employee) {
			frm.call("set_feedback_criteria", () => {
				frm.refresh_field("feedback_ratings");
			});
		}
	},
});
