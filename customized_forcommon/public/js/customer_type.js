frappe.ui.form.on('Customer', {
    onload: function (frm) {
        const field = frm.fields_dict.customer_type;
        const new_option1 = 'Foreign';
        const new_option2 = 'Local';

        if (!field.df.options.includes(new_option1)) {
            field.df.options += '\n' + new_option1;
            field.refresh();
        }
        if (!field.df.options.includes(new_option2)) {
            field.df.options += '\n' + new_option2;
            field.refresh();
        }


        frm.set_df_property('tax_id', 'label', "TIN Number");
        frm.refresh_field('tax_id');

    }
})