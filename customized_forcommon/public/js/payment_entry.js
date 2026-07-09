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
        toggle_lc_number(frm);
    },
});

function toggle_lc_number(frm) {
    let has_invoice_reference = false;

    if (frm.doc.references) {
        has_invoice_reference = frm.doc.references.some(row =>
            row.reference_doctype === "Purchase Invoice"
        );
    }
    if (has_invoice_reference) {
        frm.set_value("custom_lc_number", "")
        frm.set_df_property("custom_lc_number", "hidden", 1);
    } else {
        frm.set_df_property("custom_lc_number", "hidden", 0);

    }
}