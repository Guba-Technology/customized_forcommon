frappe.ui.form.on("Bank Transaction", {
    refresh(frm) {
        customized_forcommon.setup_reverse_bank_reconciliation(frm);
    }
});