frappe.ui.form.on("Company", {
    setup(frm) {
        frm.set_query("custom_project_advance_receivable_account", () => ({
            filters: {
                account_type: "Receivable"
            }
        }));
    }
});