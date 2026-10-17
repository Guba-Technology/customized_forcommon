// Copyright (c) 2026, Guba Technology

frappe.ui.form.on("Tender Specification", {
	refresh: function (frm) {
		if (frm.doc.status === "Locked") {
			frm.disable_save();
			frm.set_read_only();
		}
	},

	get_template_items: function (frm) {
		if (!frm.doc.request_for_quotation) {
			frappe.msgprint(__("Please select a Request for Quotation first."));
			return;
		}

		frappe.confirm(
			__("This will replace the current Criteria rows with the items and templates of the Request for Quotation. Continue?"),
			() => {
				frappe.call({
					method: "customized_forcommon.common_customization.doctype.tender_specification.tender_specification.get_template_items",
					args: { request_for_quotation: frm.doc.request_for_quotation },
					callback: function (r) {
						if (!r.message) {
							return;
						}
						frm.clear_table("criteria");
						r.message.forEach((row) => {
							let child = frm.add_child("criteria");
							child.item = row.item;
							child.component = row.component;
							child.recommended_spec = row.recommended_spec;
							child.merit_points = row.merit_points;
						});
						frm.refresh_field("criteria");
						frm.dirty();
						frm.trigger("show_item_totals");
					},
				});
			}
		);
	},

	show_item_totals: function (frm) {
		let totals = {};
		(frm.doc.criteria || []).forEach((row) => {
			if (!row.item) return;
			totals[row.item] = (totals[row.item] || 0) + (row.merit_points || 0);
		});
		let messages = Object.keys(totals).map((item) => `${item}: ${totals[item]} / 100`);
		if (messages.length) {
			frappe.msgprint({
				title: __("Points Per Item"),
				message: messages.join("<br>"),
				indicator: "blue",
			});
		}
	},
});

frappe.ui.form.on("Tender Specification Criteria", {
	merit_points: function (frm) {
		frm.trigger("show_item_totals");
	},
});
