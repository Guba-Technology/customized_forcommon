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
                () => {
                    frappe.model.open_mapped_doc({
                        method: "erpnext.stock.doctype.material_request.material_request.make_purchase_order",
                        frm: frm,
                        args: { default_supplier: null },
                        run_link_triggers: true,
                    });
                },
                __("Create")
            );
            frm.page.set_inner_btn_group_as_primary(__("Create"));
        }
    }

});
