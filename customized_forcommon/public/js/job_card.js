frappe.ui.form.on('Job Card', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {

            frm.add_custom_button(__('View Ledger'), function() {

                frappe.route_options = {
                    "voucher_no": frm.doc.name,
                    "company": frm.doc.company,
                    "from_date": frappe.datetime.add_months(frm.doc.posting_date, -1),
                    "to_date": frappe.datetime.add_months(frm.doc.posting_date, 1)
                };

                frappe.set_route("query-report", "General Ledger");

            }, __('Accounting'));
        }
    }
});