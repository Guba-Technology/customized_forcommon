frappe.ui.form.on('Stock Entry', {
    onload: function (frm) {
       show_approved_by(frm);
       toggle_button_css(frm);
    },

    stock_entry_type: function (frm) {
                show_approved_by(frm);
                toggle_button_css(frm);
    },


    refresh: function (frm) {
show_approved_by(frm);   
toggle_button_css(frm); 
}
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
function toggle_button_css(frm) {
  let $menu_item = $(frm.wrapper).find('.dropdown-item[data-label="Material%20Request"]');
    let $create_group = $(frm.wrapper).find('.inner-group-button[data-label="Create"]');
    if (frm.doc.stock_entry_type === "Material Issue for Transfer") {
        $menu_item.hide();
        $create_group.hide(); 
    } else {
        $menu_item.show();
        $create_group.show(); 
    }
}