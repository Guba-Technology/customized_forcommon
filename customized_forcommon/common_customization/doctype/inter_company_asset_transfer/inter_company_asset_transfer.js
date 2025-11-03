frappe.ui.form.on('Inter Company Asset Transfer', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('View General Ledger'), function() {
                frappe.route_options = {
                    voucher_type: 'Inter Company Asset Transfer',
                    voucher_no: frm.doc.name
                };
                frappe.set_route('query-report', 'General Ledger');
            }, __('View'));
        }
    }
});
