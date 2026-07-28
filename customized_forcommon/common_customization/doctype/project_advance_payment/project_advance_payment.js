// Copyright (c) 2026, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project Advance Payment", {
    onload(frm) {
        if (frm.is_new() && !frm.__initialized) {

            frm.__initialized = true;
            frm.set_value({
                advance_paid: 0,
                status: "Open",
                amended_from: null,
                created_advance_payment_entry: null

            });
            (frm.doc.payment_terms || []).forEach((row) => {
                row.created_purchase_invoice = null;
                row.invoice_created = 0;
            });
            frm.refresh_field("payment_terms");

            frm.clear_table("recovery_details");
            frm.refresh_field("recovery_details");


            frm.refresh_fields();

        }
    },
    setup(frm) {
        frappe.realtime.on("project_advance_payment_updated", (data) => {
            if (data.name === frm.doc.name) {
                frm.reload_doc();
            }
        });
    },
    refresh(frm) {

        // Inject dynamic CSS targeting only the Payment Entry and Purchase Invoice '+' button
        frappe.dom.set_style(`
            :is([data-doctype="Payment Entry"], [data-doctype="Purchase Invoice"]) .btn-new {
                display: none !important;
            }
        `);

        if (frm.doc.docstatus === 1) {
            if (!frm.doc.advance_paid) {
                frm.add_custom_button(__("Advance Payment"), () => {
                    frappe.model.open_mapped_doc({
                        method: "customized_forcommon.common_customization.doctype.project_advance_payment.project_advance_payment.make_payment_entry",
                        frm: frm
                    });

                }, __("Create"));
            }
            (frm.doc.payment_terms || []).forEach((row) => {
                if (frm.doc.advance_paid && row.payment_term && row.invoice_created === 0) {
                    frm.add_custom_button(
                        `Purchase Invoice for ${row.payment_term}`,
                        () => {
                            frappe.call({
                                method: "customized_forcommon.common_customization.doctype.project_advance_payment.project_advance_payment.make_purchase_invoice", // Update path to your python function
                                args: {
                                    source_name: frm.doc.name,
                                    payment_term: row.payment_term,
                                    rate: row.amount || 0
                                },
                                callback: function (r) {
                                    if (r.message) {
                                        // Route directly to the prepared form in memory
                                        var doc = frappe.model.sync(r.message);
                                        frappe.set_route("Form", doc[0].doctype, doc[0].name);
                                    }
                                }
                            });
                        },
                        __("Create")
                    );
                }
            });
        }

    },
});
