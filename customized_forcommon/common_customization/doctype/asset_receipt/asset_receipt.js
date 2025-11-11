frappe.ui.form.on('Asset Receipt', {
    refresh(frm) {
        // If location is filled but status still pending, suggest next step
        if (frm.doc.status === "In Transit" && frm.doc.location) {
            frm.set_value("status", "Received");
        }

        // Show Create Asset button only when ready
        if (frm.doc.status === "Received") {
            frm.add_custom_button(__('Create Asset'), () => {
                frappe.call({
                    method: "customized_forcommon.common_customization.doctype.asset_receipt.asset_receipt.create_asset_from_receipt",
                    args: { receipt_name: frm.doc.name },
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.msgprint(__('Asset created successfully: ') + r.message);
                            frm.reload_doc();
                        }
                    }
                });
            }).addClass('btn-primary');
        }
    }
});
