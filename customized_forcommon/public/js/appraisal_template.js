frappe.ui.form.on("Appraisal Template", {
    onload: function(frm) {
        const style = document.createElement("style");
        style.innerHTML = `
            /* Hide the standard row index */
            .grid-row .row-index,
            .grid-heading-row .row-index {
                display: none !important;
            }
            /* Hide the Rating stars */
            [data-fieldname="rating"], 
            .modal-body [data-fieldname="rating"] {
                display: none !important;
            }
            /* Make the custom number column stand out slightly */
            [data-fieldname="custom_no"] {
                font-weight: bold;
                color: #525252;
                width: 40px !important;
            }
        `;
        document.head.appendChild(style);
        toggle_child_tables(frm);
    },

    refresh: function(frm) {
        refresh_all_custom_numbers(frm);
    },

    before_save: function(frm) {
        sync_custom_score_to_rating(frm);
        refresh_all_custom_numbers(frm);
    },

    custom_criteria_for: toggle_child_tables
});

frappe.ui.form.on("Employee Feedback Rating", { 
    // Validation: Ensure Score doesn't exceed Weightage
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
    custom_self_appraisal_rating_criteria_add: (frm) => refresh_custom_numbers(frm, "custom_self_appraisal_rating_criteria"),
    custom_self_appraisal_rating_criteria_remove: (frm) => refresh_custom_numbers(frm, "custom_self_appraisal_rating_criteria")
});

// Helper: Calculate single row rating (Scale 0 to 1)
function calculate_row_rating(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    if (row.custom_score && row.per_weightage && parseFloat(row.per_weightage) > 0) {
        row.rating = parseFloat(row.custom_score) / parseFloat(row.per_weightage);
    } else {
        row.rating = 0;
    }
    // Refresh only the specific grids to keep UI fast
    frm.fields_dict["rating_criteria"].grid.refresh();
    frm.fields_dict["custom_self_appraisal_rating_criteria"].grid.refresh();
}

// Helper: Global Sync
function sync_custom_score_to_rating(frm) {
    ["rating_criteria", "custom_self_appraisal_rating_criteria"].forEach(table => {
        (frm.doc[table] || []).forEach(row => {
            if (row.custom_score && row.per_weightage && parseFloat(row.per_weightage) > 0) {
                row.rating = parseFloat(row.custom_score) / parseFloat(row.per_weightage);
            }
        });
    });
}

function toggle_child_tables(frm) {
    const config = {
        "Performance Feedback": { show: ["rating_criteria"], hide: ["custom_self_appraisal_rating_criteria"] },
        "Self Appraisal": { show: ["custom_self_appraisal_rating_criteria"], hide: ["rating_criteria"] }
    }[frm.doc.custom_criteria_for];

    if (config) {
        config.show.forEach(f => frm.set_df_property(f, "hidden", false));
        config.hide.forEach(f => frm.set_df_property(f, "hidden", true));
    }
}

function refresh_custom_numbers(frm, table_field) {
    (frm.doc[table_field] || []).forEach((row, index) => {
        row.custom_no = (index + 1).toString().padStart(2, '0');
    });
    frm.refresh_field(table_field);
}

function refresh_all_custom_numbers(frm) {
    refresh_custom_numbers(frm, "rating_criteria");
    refresh_custom_numbers(frm, "custom_self_appraisal_rating_criteria");
}