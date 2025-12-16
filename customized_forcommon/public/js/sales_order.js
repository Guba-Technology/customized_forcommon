frappe.ui.form.on("Sales Order", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button("Agreement", () => {
                frappe.new_doc("Agreement", {
                    // item: r.message.item_code
                });

            }, "Create");
        }
    }
});
