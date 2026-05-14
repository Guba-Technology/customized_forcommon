frappe.ui.form.on('System Settings', {
    refresh(frm) {

        frm.set_df_property("disable_system_update_notification", "hidden", 1);
        frm.set_df_property("disable_change_log_notification", "hidden", 1);

        frm.set_df_property("disable_system_update_notification", "read_only", 1);
        frm.set_df_property("disable_change_log_notification", "read_only", 1);
    }
});