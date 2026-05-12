frappe.ui.form.on("User", {
    refresh(frm) {
        frm.toggle_display("roles", true);
        frm.toggle_display("permissions", true);
    }
});