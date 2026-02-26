frappe.ui.form.on("Material Request", {
    refresh(frm) {
        if (frm.doc.material_request_type === "Material Cost") {
            frm.add_custom_button("BOM", () => {
                frappe.call({
                    method: "customized_forcommon.api.get_item_for_bom",
                    args: {
                        material_request: frm.doc.name
                    },
                    callback: function (r) {
                        if (r.message) {
                            if (r.message.message) {
                                frappe.msgprint(r.message.message);
                            }
                            frappe.new_doc("BOM", {
                                item: r.message.item_code
                            });
                        } else {
                            frappe.msgprint("No item found.");
                        }
                    }
                });
            }, "Create");
        }

        if (frm.doc.docstatus === 1 && frm.doc.material_request_type === "Purchase") {
            frm.remove_custom_button("Purchase Order", "Create");

            frm.add_custom_button(
                __("Purchase Order"),
                () => frm.events.make_purchase_order_direct(frm),
                __("Create")
            );

            frm.page.set_inner_btn_group_as_primary(__("Create"));
        }
    },

    make_purchase_order_direct: function (frm) {
        // Skip the supplier prompt and call the server directly
        frappe.call({
            method: "erpnext.stock.doctype.material_request.material_request.make_purchase_order",
            args: {
                source_name: frm.doc.name,
                target_doc: null,
                default_supplier: null, // equivalent to skipping supplier selection
            },
            callback: function (r) {
                if (!r.exc) {
                    // Open the mapped Purchase Order in a new form
                    frappe.model.sync(r.message);
                    frappe.set_route("Form", r.message.doctype, r.message.name);
                } else {
                    frappe.msgprint(__("Failed to create Purchase Order"));
                }
            },
        });
    }

});
