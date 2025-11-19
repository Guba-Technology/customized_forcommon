frappe.ui.form.on("Asset", {
    before_save(frm) {
        if (!frm.doc.purchase_date) {
            frm.doc.purchase_date = frappe.datetime.get_today();
        }

        if (!frm.doc.available_for_use_date) {
            frm.doc.available_for_use_date = frm.doc.purchase_date;
        }

        if (!frm.doc.gross_purchase_amount) {
            frm.doc.gross_purchase_amount = 0.0;
        }
    }
});
