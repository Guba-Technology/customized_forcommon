// Copyright (c) 2025, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on('Max User Restriction', {
    refresh: function (frm) {
        // Only override if the document is in Draft state and not new
        if (frm.doc.docstatus === 0 && !frm.is_new()) {
            frm.page.set_primary_action(__('Submit'), function () {

                frappe.confirm(
                    'Submit to confirm Max User Restriction?',
                    () => {
                        // If Yes: Bypass all client-side checks and call the submit directly
                        frappe.call({
                            method: "frappe.client.submit",
                            args: {
                                doc: frm.doc
                            },
                            callback: function (r) {
                                if (!r.exc) {
                                    frm.reload_doc();
                                }
                            }
                        });
                    },
                    () => {
                        // If No: Do nothing, stays in Draft
                        frappe.show_alert({ message: __('Cancelled'), indicator: 'orange' });
                    }
                );
            });
        }
    }
});