frappe.ui.form.on('Interview Round', {
    custom_expected_average_rating: function(frm) {
    let rating = 0;
    if (frm.doc.custom_expected_average_rating > 100) {
        frm.set_value('custom_expected_average_rating', 100);
        frm.refresh_field('custom_expected_average_rating');
        frappe.msgprint("Expected Average Rating cannot be greater than 100 <br> Setting to 100");

        rating = 1;
    }
    if (frm.doc.custom_expected_average_rating) {
        rating = parseFloat(frm.doc.custom_expected_average_rating) / 100;
    }
    frm.set_value('expected_average_rating', rating);
    frm.refresh_field('expected_average_rating');
    
}
});