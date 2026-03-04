frappe.ui.form.on('Item', {
    refresh(frm) {
        toggle_fixed_asset(frm);
    },

    is_stock_item(frm) {
        toggle_fixed_asset(frm);
    }
});

function toggle_fixed_asset(frm) {
    if (frm.doc.is_stock_item == 1) {
        frm.set_df_property('is_fixed_asset', 'hidden', 1);
    } else {
        frm.set_df_property('is_fixed_asset', 'hidden', 0);
    }
}