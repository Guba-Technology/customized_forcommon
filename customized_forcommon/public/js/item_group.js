frappe.ui.form.on("Item Group", {
    setup(frm) {
        frm.set_query(
            "custom_default_inventory_account",
            "item_group_defaults",
            function (doc, cdt, cdn) {
                let row = locals[cdt][cdn];

                return {
                    filters: {
                        company: row.company,
                        account_type: "Stock",
                        is_group: 0
                    }
                };
            }
        );
    }
});