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
    }
});
