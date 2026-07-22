// Create button from Purchase Receipt
frappe.ui.form.on("Landed Cost Voucher", {

    onload_post_render(frm) {

        if (!frm.doc.purchase_receipts ||
            !frm.doc.purchase_receipts.length) {
            return;
        }


        let row = frm.doc.purchase_receipts[0];


        // wait until mapped values are loaded
        frappe.after_ajax(() => {

            fetch_lc_costs(frm, row);

        });

    }

});

// Manual adding from child table
frappe.ui.form.on("Landed Cost Purchase Receipt", {

    receipt_document(frm, cdt, cdn) {

        let row = locals[cdt][cdn];

        fetch_lc_costs(frm, row);

    }

});


function fetch_lc_costs(frm, row) {

    if (
        !row ||
        row.receipt_document_type !== "Purchase Receipt" ||
        !row.receipt_document
    ) {
        return;
    }


    frappe.call({

        method: "customized_forcommon.api.get_lc_invoice_and_payment_entry_costs",

        args: {
            receipt_document_type: row.receipt_document_type,
            receipt_document: row.receipt_document
        },

        callback(r) {

            if (!r.message || !r.message.length) {
                return;
            }


            // Remove old generated rows only if needed
            frm.clear_table("taxes");


            r.message.forEach(item => {

                let tax_row = frm.add_child("taxes");

                tax_row.description = item.description;
                tax_row.amount = item.amount;
                tax_row.expense_account = item.expense_account;

            });


            frm.refresh_field("taxes");

        }
    });
}


