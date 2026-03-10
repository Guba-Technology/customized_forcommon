frappe.ui.form.on('Stock Entry', {
    onload: function (frm) {
       show_approved_by(frm);
    },

    stock_entry_type: function (frm) {
                show_approved_by(frm);
    },


    refresh: function (frm) {
show_approved_by(frm);    }
});

function show_approved_by(frm) {
    if (frm.doc.stock_entry_type.toLowerCase().includes("disposal")) {
        frm.set_df_property("custom_approved_by", "hidden", 0);
        frm.set_df_property("custom_disposal_account", "hidden", 0);
    } else {
        frm.set_df_property("custom_approved_by", "hidden", 1);
        frm.set_df_property("custom_disposal_account", "hidden", 1);
    }
    frm.refresh_field("custom_approved_by");
    frm.refresh_field("custom_disposal_account");
}