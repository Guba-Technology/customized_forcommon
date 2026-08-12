frappe.ui.form.on("Payroll Entry", {
    setup(frm) {
        frm.set_query("custom_cash_account", () => ({
            filters: {
                account_type: "Cash",
                company: frm.doc.company,
                is_group: 0,
            }
        }));
    },
    refresh(frm) {
        // Show button only if submitted (docstatus === 1) and Cash Entry not created yet
        if (!frm.doc.custom_cash_entry_created && frm.doc.docstatus === 1 && frm.doc.salary_slips_created === 1 && frm.doc.salary_slips_submitted === 1) {
            frm.add_custom_button(__('Cash Entry'), function () {
                frappe.call({
                    // Replace with your actual Python dot-path
                    method: "customized_forcommon.api.make_cash_journal_entry",
                    args: {
                        doc_name: frm.doc.name
                    },
                    freeze: true,
                    freeze_message: __('Creating Journal Entry...'),
                    callback: function (r) {
                        if (r.message) {
                            // Reload form to hide the button since custom_cash_entry_created will now be 1
                            frm.reload_doc();

                            frappe.msgprint({
                                title: __('Success'),
                                indicator: 'green',
                                message: __('Draft Journal Entry <a href="/app/journal-entry/{0}"><b>{0}</b></a> created successfully.', [r.message])
                            });
                        }
                    }
                });
            });
        }
    }

});