frappe.ui.form.on("Purchase Order", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(
                __("Employee Advance"),
                function () {
                    frappe.call({
                        method: "customized_forcommon.api.get_data_from_purchase_order",
                        args: {
                            purchase_order_doc: frm.doc.name
                        },
                        callback: function (r) {
                            if (!r.exc && r.message) {
                                const { employee, date, company } = r.message;

                                // Open new Employee Advance form
                                frappe.new_doc("Employee Advance", {
                                    employee: employee,
                                    posting_date: date,
                                    company: company,
                                    custom_advance_type: "For Purchase",
                                    reference_doctype: "Purchase Order",
                                    custom_purchase_order_id: frm.doc.name,
                                    advance_amount: frm.doc.grand_total,
                                    purpose: "Purchase"
                                });
                            }
                        }
                    });
                },
                __("Create") // puts button under Create menu
            );
        }
    }
});

frappe.ui.form.on("Purchase Order Item", {
    // 🔹 Trigger when Item Code, Qty, or Rate changes
    item_code: function (frm, cdt, cdn) {
        update_item_taxes(frm, cdt, cdn);
    },
    qty: function (frm, cdt, cdn) {
        update_item_taxes(frm, cdt, cdn);
    },
    rate: function (frm, cdt, cdn) {
        update_item_taxes(frm, cdt, cdn);
    },
});

// 🔹 Shared function to handle tax update logic
function update_item_taxes(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (!row.item_code) return;

    // Calculate net amount
    let net_amount = (row.qty || 0) * (row.rate || 0);

    frappe.call({
        method: "customized_forcommon.api.get_item_tax_accounts",
        args: {
            item_code: row.item_code,
            company: frm.doc.company,
            net_amount: net_amount,
            posting_date: frm.doc.transaction_date,
        },
        callback: function (r) {
            if (!r.message) r.message = [];

            // Remove existing taxes related to this item before re-adding
            frm.doc.taxes = frm.doc.taxes.filter(
                t => !t.description?.includes("(" + row.item_code + ")")
            );

            // Add applicable taxes
            r.message.forEach(tax => {
                let existing = frm.doc.taxes.find(t => t.account_head === tax.account);
                if (!existing) {
                    let child = frm.add_child("taxes");
                    child.charge_type = "On Net Total";
                    child.account_head = tax.account;
                    child.rate = tax.rate;
                    child.description = `${tax.account_name} (${row.item_code})`;

                    frappe.model.set_value(child.doctype, child.name, "rate", tax.rate);
                }
            });

            frm.refresh_field("taxes");
            frm.script_manager.trigger("calculate_taxes_and_totals");
        },
    });
}