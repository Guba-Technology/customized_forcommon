frappe.ui.form.on("Sales Order", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button("Agreement", () => {
                frappe.call({
                    method: "customized_forcommon.api.get_sales_order_data",
                    args: {
                        sales_order_doc: frm.doc.name
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
                            frappe.new_doc("Agreement", {
                                buyer: r.message.customer,
                                sales_order: frm.doc.name,
                                agreement_item: agreement_items
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
