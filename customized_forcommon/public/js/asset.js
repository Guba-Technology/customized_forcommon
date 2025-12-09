frappe.ui.form.on('Asset', {
    refresh(frm) {
        if (frm.doc.status === "Borrowed") {
            frm.page.set_indicator('Borrowed', 'orange');
        }
        if (frm.doc.status === "Borrowed") {
            frm.add_custom_button("Return Asset", function () {
                frappe.confirm(
                    __("Are you sure you want to return this asset?"),
                    () => {
                frappe.call({
                    method: "customized_forcommon.common_customization.doctype.asset_borrowing.asset_borrowing.return_asset",
                    args: {
                        asset_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.msgprint("Asset Returned");
                            frm.reload_doc();
                        }
                    }
                });
                    },
                    () => {
                        // frappe.msgprint(__("Return cancelled"));
                    }
                );
            }).addClass("btn-primary");
        }
    }
});
