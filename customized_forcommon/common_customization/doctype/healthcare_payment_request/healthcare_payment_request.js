// Copyright (c) 2026, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("Healthcare Payment Request", {
	service_amount(frm) {
		calculate_contribution(frm);
	},
	company_contribution_(frm) {
		calculate_contribution(frm);
	},
	setup(frm) {
		frm.set_query("employee", () => {
			return { filters: { company: frm.doc.company } };
		});
	},
	// refresh(frm) {
	// 	if (frm.doc.docstatus === 1 && frm.doc.payment_by === "Company") {
	// 		frm.add_custom_button(__("Process Due Deductions"), () => {
	// 			frappe.call({
	// 				method:
	// 					"customized_forcommon.common_customization.doctype.healthcare_payment_request.healthcare_payment_request.create_due_additional_salaries",
	// 				args: { healthcare_payment_request: frm.doc.name },
	// 				freeze: true,
	// 				callback: () => frm.reload_doc(),
	// 			});
	// 		});
	// 	}
	// },
});

function calculate_contribution(frm) {
	if (!frm.doc.service_amount) return;
	const pct = flt(frm.doc.company_contribution_) || 0;
	const company_amt = flt((frm.doc.service_amount * pct) / 100, precision("company_contribution_amount"));
	frm.set_value("company_contribution_amount", company_amt);
	frm.set_value("employee_contribution_amount", flt(frm.doc.service_amount - company_amt));
}
