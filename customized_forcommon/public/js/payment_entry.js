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
     paid_from: function(frm) {
        if(frm.doc.paid_from) {
            frappe.call({
                method: "customized_forcommon.custom_script.payment_entry.get_cash_employees",
                args: { paid_from_account: frm.doc.paid_from },
                callback: function(r) {
                    if(r.message) {
                        frm.set_query("paid_by", function() {
                            return { filters: { name: ["in", r.message] } };
                        });
                    }
                }
            });
        }
    }
});
