// ============================================================
// ONLY EXTENDS ORIGINAL ERPNext Payment Request JS
// Does NOT override refresh, onload, etc. → 100% safe
// ============================================================

frappe.ui.form.on("Payment Request", {
    // === 1. Run AFTER the original refresh (priority 100) ===
    refresh: function(frm) {

        if (frm.doc.payment_request_type === "Internal Transfer") {
            // Hide Party fields
            frm.toggle_display(["party_type", "party"], false);
            frm.toggle_reqd(["party_type", "party"], false);

            // Show + Require To Account
            frm.toggle_display("paid_to", true);
            frm.toggle_reqd("paid_to", true);

            // Change label: Payment Account → From Account
            frm.fields_dict.payment_account.df.label = "From Account";
            frm.refresh_field("payment_account");

            // Hide irrelevant fields
            frm.toggle_display(["payment_gateway_account", "payment_gateway", "is_a_subscription"], false);

            // Add Create Payment Entry button (only if not already added by core)
            if (!frm.doc.__islocal && ["Draft", "Initiated"].includes(frm.doc.status)) {
                if (!frm.page.btn_group.find('.btn:contains("Create Payment Entry")').length) {
                    frm.add_custom_button(__("Create Payment Entry"), function() {
                        frm.trigger("make_payment_entry");
                    }, __("Actions")).addClass("btn-primary");
                }
            }
        }
    },

    // === 2. Trigger on type change ===
    payment_request_type: function(frm) {
        // Re-run refresh logic when type changes
        setTimeout(() => frm.trigger("refresh"), 100);
    },

    // === 3. Make Payment Entry (reuses core method safely) ===
    make_payment_entry: function(frm) {
        frappe.call({
            method: "erpnext.accounts.doctype.payment_request.payment_request.make_payment_entry",
            args: { docname: frm.doc.name },
            freeze: true,
            freeze_message: __("Creating Payment Entry..."),
            callback: function(r) {
                if (!r.exc && r.message) {
                    frappe.set_route("Form", r.message.doctype, r.message.name);
                }
            }
        });
    }
});