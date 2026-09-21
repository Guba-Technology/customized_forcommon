// Copyright (c) 2026, Guba Technology
// License: MIT

frappe.ui.form.on("Training Impact Assessment", {
	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(
				__("Create Training Assessment Response"),
				function () {
					frappe.confirm(
						__(
							"This will create a Trainee response and a Manager response for every assigned employee (existing responses are skipped). Continue?"
						),
						function () {
							frm.call("create_assessment_responses").then((r) => {
								frm.reload_doc();
							});
						}
					);
				},
				__("Actions")
			);

			frm.add_custom_button(
				__("View Responses"),
				function () {
					frappe.set_route("List", "Training Assessment Response", {
						training_impact_assessment: frm.doc.name,
					});
				},
				__("View")
			);

			frm.add_custom_button(
				__("View Report"),
				function () {
					frappe.db
						.exists("Training Impact Assessment Report", frm.doc.name)
						.then((exists) => {
							if (exists) {
								frappe.set_route("Form", "Training Impact Assessment Report", frm.doc.name);
							} else {
								frappe.msgprint(
									__("No report has been generated yet. Submit at least one response first.")
								);
							}
						});
				},
				__("View")
			);
		}
	},
	company: apply_employee_filters,
	designation: apply_employee_filters,
	branch: apply_employee_filters,
	grade: apply_employee_filters,
	department: apply_employee_filters,
	shift: apply_employee_filters,
});
function apply_employee_filters(frm) {
	// Debounce so rapid changes (e.g. clearing one filter then picking another)
	// don't fire multiple overlapping calls.
	clearTimeout(frm.__employee_filter_timeout);
	frm.__employee_filter_timeout = setTimeout(() => fetch_and_apply_employees(frm), 300);
}

function fetch_and_apply_employees(frm) {
	const filters = {
		company: frm.doc.company,
		designation: frm.doc.designation,
		branch: frm.doc.branch,
		grade: frm.doc.grade,
		department: frm.doc.department,
		shift: frm.doc.shift,
	};

	// If every filter is empty, don't wipe out a manually built list.
	const has_any_filter = Object.values(filters).some((v) => !!v);
	if (!has_any_filter) {
		return;
	}

	frappe.call({
		
        method:"customized_forcommon.common_customization.doctype.training_impact_assessment.test_training_impact_assessment.get_filtered_employees",
		args: {filters: filters},
		callback: function (r) {
			const employees = r.message || [];

			// Table always mirrors the current filter result set.
			frm.clear_table("assigned_employees");

			employees.forEach((emp) => {
				const row = frm.add_child("assigned_employees");
				row.employee = emp.employee;
				row.employee_name = emp.employee_name;
				row.department = emp.department;
				row.designation = emp.designation;
				// row.manager = emp.manager;
			});

			frm.refresh_field("assigned_employees");

			frappe.show_alert({
				message: employees.length
					? __("{0} employee(s) matched the filter", [employees.length])
					: __("No employees matched the filter"),
				indicator: employees.length ? "green" : "orange",
			});
		},
	});
}