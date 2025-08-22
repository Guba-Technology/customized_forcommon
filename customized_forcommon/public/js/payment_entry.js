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
    }
});
