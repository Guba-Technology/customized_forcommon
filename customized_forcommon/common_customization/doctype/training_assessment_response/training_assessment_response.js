//Copyright (c) 2025, Guba Technology and Contributors

frappe.ui.form.on("Training Assessment Response", {
	setup: function (frm) {
		// Trainee Name may only be one of the employees assigned to the selected
		// Training Impact Assessment (Assigned Employees child table).
		frm.set_query("trainee_name", function () {
			if (!frm.doc.training_impact_assessment) {
				return { filters: { name: ["in", []] } }; // nothing to pick until an assessment is set
			}
			return {
				query:
					"customized_forcommon.common_customization.doctype.training_assessment_response.training_assessment_response.get_assigned_employees",
				filters: {
					training_impact_assessment: frm.doc.training_impact_assessment,
					column: "employee",
				},
			};
		});

	
		frm.set_query("evaluator", function () {
			if (!frm.doc.training_impact_assessment) {
				return { filters: { name: ["in", []] } };
			}
			return {
				query:
					"customized_forcommon.common_customization.doctype.training_assessment_response.training_assessment_response.get_assigned_employees",
				filters: {
					training_impact_assessment: frm.doc.training_impact_assessment,
					column: frm.doc.evaluator_type === "Manager" ? "manager" : "employee",
				},
			};
		});
	},

	refresh: function (frm) {
		if (frm.doc.docstatus === 1) {
			frm.dashboard.set_headline(
				__("Submitted. This response has been included in the Training Impact Assessment Report.")
			);
		}
	},

	training_impact_assessment: function (frm) {
		// Clear selections that may no longer be valid under the new assessment's
		// Assigned Employees list, then re-fetch the default assessment date.
		frm.set_value("trainee_name", "");
		frm.set_value("evaluator", "");

		if (frm.doc.training_impact_assessment && !frm.doc.assessment_date) {
			frappe.db
				.get_value("Training Impact Assessment", frm.doc.training_impact_assessment, "training_date")
				.then((r) => {
					if (r.message && r.message.training_date) {
						frm.set_value("assessment_date", r.message.training_date);
					}
				});
		}
	},

	evaluator_type: function (frm) {
		// The valid Evaluator set (employee vs. manager) depends on evaluator_type.
		frm.set_value("evaluator", "");
	},

	trainee_name: function (frm) {
		// If evaluating as Trainee, Evaluator is always the trainee themselves.
		if (frm.doc.evaluator_type === "Trainee") {
			frm.set_value("evaluator", frm.doc.trainee_name);
		} else {
			frm.set_value("evaluator", "");
		}
	},
});
