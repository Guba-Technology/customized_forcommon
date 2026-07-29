frappe.provide("customized_forcommon");

customized_forcommon.setup_reverse_bank_reconciliation = function (frm) {
    if (frm.doc.docstatus !== 1) {
        return;
    }

    frappe.call({
        method: "customized_forcommon.api.check_reconciliation_status",
        args: {
            voucher_type: frm.doc.doctype,
            voucher_no: frm.doc.name
        },
        callback(r) {
            if (
                r.message &&
                r.message.is_reconciled
            ) {
                frm.add_custom_button(
                    __("Reverse Bank Reconciliation"),
                    function () {
                        let dialog = new frappe.ui.Dialog({
                            title: __("Reverse Bank Reconciliation"),
                            fields: [
                                {
                                    fieldname: "clearance_date",
                                    label: __("Original Clearance Date"),
                                    fieldtype: "Data",
                                    read_only: 1,
                                    default: r.message.clearance_date
                                },
                                {
                                    fieldname: "reason",
                                    label: __("Reversal Reason"),
                                    fieldtype: "Small Text",
                                    reqd: 1
                                }
                            ],
                            primary_action_label:
                                __("Reverse"),
                            primary_action(values) {
                                frappe.call({
                                    method:
                                        "customized_forcommon.api.reverse_bank_reconciliation",
                                    args: {
                                        voucher_type: frm.doc.doctype,
                                        voucher_no: frm.doc.name,
                                        reversal_reason: values.reason
                                    },
                                    freeze: true,
                                    freeze_message:
                                        __("Reversing reconciliation..."),
                                    callback(r) {
                                        if (!r.exc) {
                                            dialog.hide();
                                            frm.reload_doc();
                                        }
                                    }
                                });
                            }
                        });
                        dialog.show();
                    },
                    __("Actions")
                );
            }
        }
    });
};