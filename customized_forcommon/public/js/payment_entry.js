frappe.ui.form.on("Payment Entry", {
     refresh(frm) {
        // Hide Paid By field if linked to Employee Advance
        const has_employee_advance = (frm.doc.references || []).some(r => r.reference_doctype === "Employee Advance");

        frm.toggle_display("paid_by", !has_employee_advance);

    },
    setup(frm) {
        // Override Paid To filter
        frm.set_query("paid_to", function () {
            frm.events.validate_company(frm);
            return {
                filters: {
                    is_group: 0,
                    company: frm.doc.company
                },
            };
        });
    },
     paid_from: function(frm) {
        if(frm.doc.paid_from) {
            frappe.call({
                method: "customized_forcommon.custom_script.payment_entry.get_cash_employees",
                args: { paid_from_account: frm.doc.paid_from },
                callback: function(r) {
                    if(r.message) {
                        frm.set_query("paid_by", function() {
                            return { filters: { name: ["in", r.message] } };
                        });
                    }
                }
            });
        }
    }
});
