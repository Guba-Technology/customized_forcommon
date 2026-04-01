frappe.ui.form.on("Employee", {
    refresh(frm) {
        frm.reload_doc();
    }
});