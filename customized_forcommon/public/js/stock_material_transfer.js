frappe.ui.form.on('Stock Entry', {
    refresh: function (frm) {
        if (frm.is_new()) {
            frm.set_value("custom_transfer_status", "Draft")
        }
        console.log("Called...")
        if (frm.doc.stock_entry_type !== "Material Transfer") return;

        // Step 1: Send to Transit
        if (frm.doc.custom_transfer_status === "Draft") {
            frm.add_custom_button(__('Send to Transit'), function () {
                frappe.call({
                    method: "customized_forcommon.api.send_to_transit",
                    args: { stock_entry: frm.doc.name },
                    callback: function (r) {
                        frm.reload_doc();
                    }
                });
            });
        }

        // Step 2: Complete Transfer
        if (frm.doc.custom_transfer_status === "Pending Receipt") {
            frm.add_custom_button(__('Complete Transfer'), function () {
                frappe.call({
                    method: "customized_forcommon.api.complete_transfer",
                    args: { stock_entry: frm.doc.name },
                    callback: function (r) {
                        frm.reload_doc();
                    }
                });
            });
        }
    }
});
