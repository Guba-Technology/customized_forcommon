frappe.ui.form.on('Interview Feedback', {

    validate: function(frm) {
        let total_score = 0;
        let row_count = frm.doc.skill_assessment ? frm.doc.skill_assessment.length : 0;
        (frm.doc.skill_assessment || []).forEach(row => {
            if (flt(row.custom_rating) > 100) {
                frappe.throw(__('Row {0}: Custom Rating ({1}) cannot exceed 100', 
                    [row.idx, row.custom_rating]));
            }
            total_score += flt(row.custom_rating);
        });

        if (row_count > 0) {
           if (total_score/row_count > 100) {
               frappe.throw(__('Total Score cannot exceed 100. Current: {0}', [total_score/row_count]));
           }
        }
    }
});

frappe.ui.form.on('Skill Assessment', {
    custom_rating: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (flt(row.custom_rating) > 100) {
            frappe.msgprint({
                title: __('Warning'),
                message: __('Custom Rating exceeds 100!'),
                indicator: 'orange'
            });
        }
        row.rating = flt(row.custom_rating) / 100;
        frm.fields_dict.skill_assessment.grid.refresh();
        calculate_total_and_average(frm);
    },
    skill_assessment_remove: function(frm) {
        calculate_total_and_average(frm);
    }
});

var calculate_total_and_average = function(frm) {
    let total_score = 0;
    let row_count = frm.doc.skill_assessment ? frm.doc.skill_assessment.length : 0;

    (frm.doc.skill_assessment || []).forEach(row => {
        total_score += flt(row.custom_rating);
    });

   total_score = total_score/ 100;
    if (row_count > 0) {
        let average = total_score / row_count;
        frm.set_value('average_rating', average);
    } else {
        frm.set_value('average_rating', 0);
    }
};
