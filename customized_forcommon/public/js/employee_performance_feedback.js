frappe.ui.form.on('Employee Performance Feedback', {
    onload: function(frm) {
        frm.get_field('feedback_ratings').grid.set_column_disp('rating', false);
    },
    validate: function(frm) {
        let total_weightage = 0;
        let total_score = 0;
        
        $.each(frm.doc.feedback_ratings || [], function(i, row) {
            total_weightage += flt(row.per_weightage);
            total_score += flt(row.custom_score);

            if (flt(row.custom_score) > flt(row.per_weightage)) {
                frappe.throw(__('Row {0}: Custom Score ({1}) cannot be greater than Weightage ({2})', 
                    [row.idx, row.custom_score, row.per_weightage]));
            }
        });

        if (total_weightage !== 100) {
            frappe.throw(__('Total Weightage must be exactly 100%. Current: {0}%', [total_weightage]));
        }

        if (total_score > 100) {
            frappe.throw(__('Total Score cannot exceed 100. Current: {0}', [total_score]));
        }
    }
});

frappe.ui.form.on('Employee Feedback Rating', {
    form_render: function(frm, cdt, cdn) {
        let child_form = frm.fields_dict['feedback_ratings'].grid.get_field('rating');
        if (child_form) {
            frm.fields_dict['feedback_ratings'].grid.toggle_display('rating', false);
        }
    },
    custom_score: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (flt(row.custom_score) > flt(row.per_weightage)) {
            frappe.msgprint({
                title: __('Warning'),
                message: __('Custom Score exceeds weightage!'),
                indicator: 'orange'
            });
        }
        calculate_total_score(frm);
    },
    feedback_ratings_remove: function(frm) {
        calculate_total_score(frm);
    }
});

var calculate_total_score = function(frm) {
    let total_score = 0;
    $.each(frm.doc.feedback_ratings || [], function(i, row) {
        total_score += flt(row.custom_score);
    });
    frm.set_value('total_score', total_score);
};