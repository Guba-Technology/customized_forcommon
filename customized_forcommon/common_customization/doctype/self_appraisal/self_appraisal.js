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

    onload(frm) {
        calculate_all_ratings(frm);
    },

    refresh(frm) {
        calculate_all_ratings(frm);
    },

    before_save(frm) {
        calculate_all_ratings(frm);
    },

    employee(frm) {
        // FIX: pass null explicitly, and clear downstream fields too
        frm.set_value("appraisal", null);
        frm.set_value("appraisal_template", null);
        frm.set_value("self_evaluation_result", []);
        frm.set_value("total_score", 0);
        frm.refresh_field("self_evaluation_result");
    },

    appraisal(frm) {
        if (frm.doc.employee && frm.doc.appraisal) {
            frm.call("set_self_appraisal_template", () => {
                frm.refresh_field("appraisal_template");
                // FIX: refresh_field does NOT fire the appraisal_template trigger.
                // Explicitly trigger it so feedback criteria actually get fetched.
                if (frm.doc.appraisal_template) {
                    frm.trigger("appraisal_template");
                } else {
                    // Template wasn't resolved server-side — make sure stale rows are gone
                    frm.set_value("self_evaluation_result", []);
                    frm.set_value("total_score", 0);
                    frm.refresh_field("self_evaluation_result");
                }
            });
        } else {
            frm.set_value("appraisal_template", null);
            frm.set_value("self_evaluation_result", []);
            frm.set_value("total_score", 0);
            frm.refresh_field("appraisal_template");
            frm.refresh_field("self_evaluation_result");
        }
    },

    appraisal_template(frm) {
        if (frm.doc.employee) {
            frm.call("set_feedback_criteria", () => {
                frm.refresh_field("self_evaluation_result");
                calculate_all_ratings(frm);
            });
        }
    },
});

frappe.ui.form.on("Employee Feedback Rating", {
    custom_score(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.custom_score > row.per_weightage) {
            frappe.msgprint(__("Score cannot be greater than Weightage ({0})", [row.per_weightage]));
            frappe.model.set_value(cdt, cdn, "custom_score", row.per_weightage);
        }
        calculate_row_rating(frm, cdt, cdn);
    },

    per_weightage(frm, cdt, cdn) {
        calculate_row_rating(frm, cdt, cdn);
    },
});

// Helper: Calculate single row rating (Scale 0 to 1)
function calculate_row_rating(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    if (row.custom_score && row.per_weightage && parseFloat(row.per_weightage) > 0) {
        row.rating = parseFloat(row.custom_score) / parseFloat(row.per_weightage);
    } else {
        row.rating = 0;
    }
    frm.fields_dict["self_evaluation_result"] && frm.fields_dict["self_evaluation_result"].grid.refresh();
    calculate_total_score(frm);
}

// Helper: Calculate rating for every row (used on load/refresh/after template load)
function calculate_all_ratings(frm) {
    (frm.doc.self_evaluation_result || []).forEach(row => {
        if (row.custom_score && row.per_weightage && parseFloat(row.per_weightage) > 0) {
            row.rating = parseFloat(row.custom_score) / parseFloat(row.per_weightage);
        } else {
            row.rating = 0;
        }
    });
    frm.fields_dict["self_evaluation_result"] && frm.fields_dict["self_evaluation_result"].grid.refresh();
    calculate_total_score(frm);
}

// Helper: Roll up total_score from row scores
function calculate_total_score(frm) {
    let rows = frm.doc.self_evaluation_result || [];
    let total = 0;
    rows.forEach(row => {
        total += parseFloat(row.custom_score) || 0;
    });
    frm.set_value("total_score", total);
}