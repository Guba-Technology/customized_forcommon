frappe.ui.form.on("Journal Entry", {
    refresh(frm) {
        customized_forcommon.setup_reverse_bank_reconciliation(frm);
    }

});