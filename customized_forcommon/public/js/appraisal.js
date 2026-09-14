frappe.ui.form.on("Appraisal", {
    onload: function(frm) {
        calculate_all_ratings(frm);
        refresh_all_custom_numbers(frm);
    },

    refresh: function(frm) {
        calculate_all_ratings(frm);
        refresh_all_custom_numbers(frm);
    },

    before_save: function(frm) {
        sync_custom_score_to_rating(frm);
        refresh_all_custom_numbers(frm);
    },
});

frappe.ui.form.on("Employee Feedback Rating", {
    custom_score: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.custom_score > row.per_weightage) {
            frappe.msgprint(__("Score cannot be greater than Weightage ({0})", [row.per_weightage]));
            frappe.model.set_value(cdt, cdn, "custom_score", row.per_weightage);
        }
        calculate_row_rating(frm, cdt, cdn);
    },

    per_weightage: function(frm, cdt, cdn) {
        calculate_row_rating(frm, cdt, cdn);
    },

    rating_criteria_add: (frm) => refresh_custom_numbers(frm, "rating_criteria"),
    rating_criteria_remove: (frm) => refresh_custom_numbers(frm, "rating_criteria"),
    self_ratings_add: (frm) => refresh_custom_numbers(frm, "self_ratings"),
    self_ratings_remove: (frm) => refresh_custom_numbers(frm, "self_ratings")
});

function calculate_row_rating(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    if (row.custom_score && row.per_weightage && parseFloat(row.per_weightage) > 0) {
        row.rating = parseFloat(row.custom_score) / parseFloat(row.per_weightage);
    } else {
        row.rating = 0;
    }
    frm.fields_dict["rating_criteria"].grid.refresh();
    frm.fields_dict["self_ratings"].grid.refresh();
}

function calculate_all_ratings(frm) {
    ["rating_criteria", "self_ratings"].forEach(table => {
        (frm.doc[table] || []).forEach(row => {
            if (row.custom_score && row.per_weightage && parseFloat(row.per_weightage) > 0) {
                row.rating = parseFloat(row.custom_score) / parseFloat(row.per_weightage);
            } else {
                row.rating = 0;
            }
        });
    });
    frm.fields_dict["rating_criteria"] && frm.fields_dict["rating_criteria"].grid.refresh();
    frm.fields_dict["self_ratings"] && frm.fields_dict["self_ratings"].grid.refresh();
}

function sync_custom_score_to_rating(frm) {
    calculate_all_ratings(frm);
    ["rating_criteria", "self_ratings"].forEach(table => {
        (frm.doc[table] || []).forEach(row => {
            row.custom_no = row.custom_no || "00";
        });
    });
}

function refresh_custom_numbers(frm, table_field) {
    (frm.doc[table_field] || []).forEach((row, index) => {
        row.custom_no = (index + 1).toString().padStart(2, '0');
        frappe.model.set_value(row.doctype, row.name, "custom_no", row.custom_no);
    });
    frm.refresh_field(table_field);
}

function refresh_all_custom_numbers(frm) {
    refresh_custom_numbers(frm, "rating_criteria");
    refresh_custom_numbers(frm, "self_ratings");
}