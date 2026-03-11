frappe.ui.form.on("Payment Request", {
    refresh(frm) {
        if (!frm.doc) return;

        // Toggle fields for Internal Transfer
        toggle_internal_transfer_fields(frm);

        // Show Internal Transfer button if type = Internal Transfer & submitted
        if (frm.doc.payment_request_type === "Internal Transfer" && frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Internal Transfer"), () => {
                frappe.call({
                    method: "erpnext.accounts.doctype.payment_request.payment_request.make_payment_entry",
                    args: { docname: frm.doc.name },
                    freeze: true,
                    freeze_message: __("Processing Internal Transfer..."),
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.model.sync(r.message);
                            frappe.set_route("Form", r.message.doctype, r.message.name);
                        }
                    }
                });
            }).addClass("btn-primary");
        }
    },

    payment_request_type(frm) {
        // Hide/show fields dynamically when type changes
        toggle_internal_transfer_fields(frm);

        // Refresh form to trigger refresh logic (adds button if Internal Transfer)
        frm.refresh();
    }
});

function toggle_internal_transfer_fields(frm) {
    const fields = [        
        "party_details",
        "subscription_section"
        
    ];

    if (frm.doc.payment_request_type === "Internal Transfer") {
        fields.forEach(f => frm.toggle_display(f, false));
    } else {
        fields.forEach(f => frm.toggle_display(f, true));
    }
}
