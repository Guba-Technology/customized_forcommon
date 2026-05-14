frappe.ui.form.on("User", {
    refresh(frm) {
        frm.set_df_property("app_section", "hidden", 1);
    }
});