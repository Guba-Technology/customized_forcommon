frappe.ui.form.on("Company", {
    setup(frm) {
        frm.set_query("custom_project_advance_receivable_account", () => ({
            filters: {
                account_type: "Receivable",
                is_group: 0,
                company: frm.doc.name,
            }
        }));
        frm.set_query("custom_profit_tax_expense_account", () => ({
            filters: {
                company: frm.doc.name,
                is_group: 0,
            }
        }));
        frm.set_query("custom_profit_tax_provision_account", () => ({
            filters: {
                company: frm.doc.name,
                is_group: 0,
            }
        }));
    }
});