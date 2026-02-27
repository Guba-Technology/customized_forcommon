frappe.ui.form.on("Supplier Quotation Item", {
    item_code: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.item_code) return;

        frappe.call({
            method: "customized_forcommon.api.get_item_tax_accounts",
            args: {
                item_code: row.item_code,
                company: frm.doc.company
            },
            callback: function (r) {
                if (!r.message || r.message.length === 0) return;

                if (!frm.doc.taxes) frm.doc.taxes = [];

                r.message.forEach(tax => {
                    let existing = frm.doc.taxes.find(t => t.account_head === tax.account);
                    if (!existing) {
                        let child = frm.add_child("taxes");
                        child.charge_type = "On Net Total";
                        child.account_head = tax.account;
                        child.rate = tax.rate;  // important for UI
                        child.description = tax.account_name + " (" + row.item_code + ")";
                        frappe.model.set_value(child.doctype, child.name, "rate", tax.rate); // forces UI refresh
                    }
                });

                frm.refresh_field("taxes");
                frm.script_manager.trigger("calculate_taxes_and_totals"); // recalc amounts
            }
        });
    }
});