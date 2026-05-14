frappe.ui.form.on("User", {
    refresh(frm) {
        frm.toggle_display("app_section", false);
    }
});