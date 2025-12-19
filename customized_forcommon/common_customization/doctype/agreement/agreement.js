// Copyright (c) 2025, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("Agreement", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button("Sales Order", () => {
                frappe.call({
                    method: "customized_forcommon.common_customization.doctype.agreement.agreement.get_data",
                    args: {
                        agreement_doc: frm.doc.name
                    },
                    callback: function (r) {
                        if (r.message) {
                            if (r.message.message) {
                                frappe.msgprint(r.message.message);
                            }

                            // Prepare child table data for Agreement
                            let agreement_items = [];
                            if (r.message.items && r.message.items.length > 0) {
                                r.message.items.forEach((item) => {
                                    agreement_items.push({
                                        item_code: item.item_code,
                                        qty: item.qty,
                                        rate: item.rate,
                                        amount: item.amount
                                    });
                                });
                            }

                            // Create new Agreement doc with buyer and agreement items
                            frappe.new_doc("Sales Order", {
                                customer: r.message.customer,
                                items: agreement_items,
                                company: r.message.company
                            });

                        } else {
                            frappe.msgprint("No data found.");
                        }
                    }
                });
            }, "Create");
        }
    }
});

frappe.ui.form.on('Agreement Item', {
    qty(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    },
    rate(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    }
});

function calculate_amount(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    row.amount = (row.qty || 0) * (row.rate || 0);
    frappe.model.set_value(cdt, cdn, 'amount', row.amount);
    frm.refresh_field('agreement_item');

}