frappe.ui.form.on("Purchase Order", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(
                __("Employee Advance"),
                function () {
                    frappe.call({
                        method: "customized_forcommon.api.get_data_from_purchase_order",
                        args: {
                            purchase_order_doc: frm.doc.name
                        },
                        callback: function (r) {
                            if (!r.exc && r.message) {
                                const { employee, date, company } = r.message;

                                // Open new Employee Advance form
                                frappe.new_doc("Employee Advance", {
                                    employee: employee,
                                    posting_date: date,
                                    company: company,
                                    custom_advance_type: "For Purchase",
                                    reference_doctype: "Purchase Order",
                                    reference_name: frm.doc.name
                                });
                            }
                        }
                    });
                },
                __("Create") // puts button under Create menu
            );
        }
    }
});