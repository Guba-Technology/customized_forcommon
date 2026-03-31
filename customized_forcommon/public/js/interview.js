frappe.ui.form.on('Interview', {
    refresh: function(frm) {
        let average_rating = frm.doc.average_rating;
        let average_rating_100 = average_rating * 100;
        frm.set_value('custom_obtained_average_rating', average_rating_100);
        frm.refresh_field('custom_obtained_average_rating');
        let expected_average_rating = frm.doc.expected_average_rating;
        let expected_average_rating_100 = expected_average_rating * 100;
        frm.set_value('custom_expected_average_rating', expected_average_rating_100);
        frm.refresh_field('custom_expected_average_rating');

    },
    
})