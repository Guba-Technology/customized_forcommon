// Copyright (c) 2025, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("Agreement", {
    refresh(frm) {

    },
});

frappe.ui.form.on('Agreement Item', {
    qty(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    },
    rate(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    }
});

function calculate_amount(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    row.amount = (row.qty || 0) * (row.rate || 0);
    frappe.model.set_value(cdt, cdn, 'amount', row.amount);
    frm.refresh_field('agreement_item');

}