frappe.ui.form.on("Purchase Invoice", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            if (frm.doc.status === "Unpaid" || frm.doc.status === "Partly Paid") {
                frm.add_custom_button("Advance Clearance", () => {
                    frappe.call({
                        method: "customized_forcommon.api.purchase_invoice_id",
                        args: {
                            purchase_invoice: frm.doc.name
                        },
                        callback: function (r) {
                            if (!r.exec && r.message) {
                                purchase_invoice_id = r.message.purchase_invoice_id
                                frappe.new_doc("Employee Advance Clearance", {
                                    purchase_invoice: purchase_invoice_id
                                });
                            }
                        }
                    });
                }, "Create");
            }
        }

    }
});
