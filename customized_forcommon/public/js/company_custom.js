frappe.ui.form.on('Company', {
    refresh: function(frm) {
        frm.set_df_property('tax_id', 'label', 'TIN');
        frm.set_df_property('tax_id', 'reqd', 1);
        frm.set_df_property('create_chart_of_accounts_based_on', 'reqd', 1);
        frm.set_df_property('registration_details','label','Registration Details (Company registration numbers for your reference. Tax numbers etc.)');
        frm.set_df_property('registration_details','description','');
        frm.refresh_field('registration_details');
        frm.refresh_field('tax_id');
        frm.refresh_field('create_chart_of_accounts_based_on');
    }
});

