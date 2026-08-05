frappe.ui.form.on("Payment Entry", {
    setup(frm) {
        // Override Paid To filter
        frm.set_query("paid_to", function () {
            frm.events.validate_company(frm);
            return {
                filters: {
                    is_group: 0,             // Only leaf accounts
                    company: frm.doc.company // Restrict to selected company
                },
            };
        });
    },
    refresh(frm) {
        customized_forcommon.setup_reverse_bank_reconciliation(frm);
    }
});


frappe.ui.form.on("Payment Entry Reference", {
    reference_name(frm, cdt, cdn) {

        let row = locals[cdt][cdn];

        if (!row.reference_doctype || !row.reference_name) {
            return;
        }

        frappe.call({
            method:
                "customized_forcommon.api.get_manual_reference_details",

            args: {
                reference_doctype: row.reference_doctype,
                reference_name: row.reference_name,
                party_account_currency:
                    frm.doc.payment_type == "Receive"
                        ? frm.doc.paid_from_account_currency
                        : frm.doc.paid_to_account_currency,

                party_type: frm.doc.party_type,
                party: frm.doc.party
            },

            callback(r) {

                if (r.message) {

                    Object.keys(r.message).forEach(field => {

                        frappe.model.set_value(
                            cdt,
                            cdn,
                            field,
                            r.message[field]
                        );

                    });


                    let allocated =
                        Math.min(
                            frm.doc.unallocated_amount || 0,
                            r.message.outstanding_amount || 0
                        );


                    frappe.model.set_value(
                        cdt,
                        cdn,
                        "allocated_amount",
                        allocated
                    );

                    frm.refresh_field("references");
                }
            }
        });
    }
});