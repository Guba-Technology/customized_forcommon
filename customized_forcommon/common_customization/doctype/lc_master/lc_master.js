// Copyright (c) 2026, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("LC Master", {
    refresh(frm) {
        toggle_empty_messages(frm);

        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Purchase Order"), () => {
                frappe.new_doc("Purchase Order", {
                    custom_lc_number: frm.doc.lc_number
                });
            },
                __("Create")
            );

            frm.add_custom_button(__("Purchase Invoice"), () => {
                frappe.new_doc("Purchase Invoice", {
                    custom_lc_number: frm.doc.lc_number
                });
            },
                __("Create")
            );
            frm.add_custom_button(__("Payment Entry"), () => {
                frappe.new_doc("Payment Entry", {
                    custom_lc_number: frm.doc.lc_number
                });
            },
                __("Create")
            );
            frm.add_custom_button(__("Purchase Receipt"), () => {
                frappe.new_doc("Purchase Receipt", {
                    custom_lc_number: frm.doc.lc_number
                });
            },
                __("Create")
            );
            frm.add_custom_button(__("Journal Entry"), () => {
                frappe.new_doc("Journal Entry", {
                    custom_lc_number: frm.doc.lc_number
                });
            },
                __("Create")
            );
        }
    }
});

function toggle_empty_messages(frm) {

    const configs = [
        {
            table: "linked_purchase_orders",
            html: "no_po_msg",
            label: "Purchase Orders"
        },
        {
            table: "linked_purchase_invoices",
            html: "no_pi_msg",
            label: "Purchase Invoices"
        },
        {
            table: "linked_purchase_receipts",
            html: "no_pr_msg",
            label: "Purchase Receipts"
        },
        {
            table: "linked_payment_entries",
            html: "no_pe_msg",
            label: "Payment Entries"
        },
        {
            table: "linked_journal_entries",
            html: "no_je_msg",
            label: "Journal Entries"
        }
    ];

    configs.forEach(cfg => {
        let has_data = (frm.doc[cfg.table] || []).length > 0;

        if (!has_data) {
            frm.fields_dict[cfg.html].$wrapper.html(`
                <div style="
                    padding: 10px;
                    border: 1px dashed #ccc;
                    border-radius: 6px;
                    background: #fafafa;
                    color: #777;
                    text-align: center;
                ">
                    No Linked ${cfg.label} Found
                </div>
            `);
        } else {
            frm.fields_dict[cfg.html].$wrapper.empty();
        }
    });
}