frappe.ui.form.on("Stock Entry", {
    refresh(frm) {

        if (
            frm.doc.docstatus === 1 &&
            frm.doc.stock_entry_type === "Material Issue"
        ) {

            frm.add_custom_button("Stock Return", () => {

                frappe.call({
                    method: "customized_forcommon.api.create_stock_return",
                    args: {
                        source_name: frm.doc.name
                    },
                    callback(r) {

                        if (!r.message) return;

                        // load document into UI (unsaved draft)
                        frappe.model.sync(r.message);

                        frappe.set_route(
                            "Form",
                            "Stock Entry",
                            r.message.name
                        );
                    }
                });

            }, __("Create"));
        }
    }
});