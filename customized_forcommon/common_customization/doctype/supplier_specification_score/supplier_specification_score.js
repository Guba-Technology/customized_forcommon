// Copyright (c) 2026, Guba Technology

frappe.ui.form.on("Supplier Specification Score", {
	refresh: function (frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__("Push to Comparison Sheet"), function () {
				frappe.call({
					method: "customized_forcommon.common_customization.doctype.supplier_specification_score.supplier_specification_score.push_specification_score",
					args: { name: frm.doc.name },
					callback: function () {
						frappe.show_alert({
							message: __("Specification result pushed."),
							indicator: "green",
						});
					},
				});
			});
		}
	},

	tender_specification: function (frm) {
		if (!frm.doc.tender_specification) {
			frm.clear_table("score_details");
			frm.refresh_field("score_details");
			return;
		}
		// Do not wipe a bidder-submitted set of offered specs.
		if (frm.doc.score_details && frm.doc.score_details.length) {
			return;
		}
		frappe.call({
			method: "customized_forcommon.common_customization.doctype.supplier_specification_score.supplier_specification_score.get_spec_criteria",
			args: { tender_specification: frm.doc.tender_specification },
			callback: function (r) {
				frm.clear_table("score_details");
				(r.message || []).forEach((row) => {
					let child = frm.add_child("score_details");
					child.item = row.item;
					child.component = row.component;
					child.recommended_spec = row.recommended_spec;
					child.max_points = row.merit_points;
				});
				frm.refresh_field("score_details");
			},
		});
	},
});

frappe.ui.form.on("Supplier Specification Score Detail", {
	points_awarded: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.points_awarded != null && row.max_points != null && row.points_awarded > row.max_points) {
			frappe.msgprint(
				__("Points Awarded cannot be more than Max Points ({0}).", [row.max_points])
			);
			frappe.model.set_value(cdt, cdn, "points_awarded", row.max_points);
		}
	},
});
