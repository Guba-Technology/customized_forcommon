frappe.ui.form.on('Employee', {

    // Triggered whenever personal_email or company_email changes
    personal_email: function(frm) {
        validate_email_field(frm, 'personal_email');
    },

    company_email: function(frm) {
        validate_email_field(frm, 'company_email');
    }
});

// Helper function to avoid repeating code
function validate_email_field(frm, fieldname) {
    const email_field = frm.fields_dict[fieldname];
    const email_value = frm.doc[fieldname];

    // Clear previous message if empty
    if (!email_value) {
        frm.set_df_property(fieldname, 'description', '');
        frm.refresh_field(fieldname);
        return;
    }

    // Email format validation
    const email_regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email_regex.test(email_value)) {
        frm.set_df_property(fieldname, 'description_html', true);
        frm.set_df_property(fieldname, 'description', '<span style="color:red">Invalid email format.</span>');
        frm.refresh_field(fieldname);
        return;
    }

    // Check if email already exists in User doctype
    frappe.db.get_list('User', {
        filters: { email: email_value },
        fields: ['name']
    }).then(users => {
        frm.set_df_property(fieldname, 'description_html', true);
        if (users.length && users[0].name !== frm.doc.name) {
            frm.set_df_property(fieldname, 'description', '<span style="color:red">This email is already used. Please choose another.</span>');
        } else {
            frm.set_df_property(fieldname, 'description', '');
        }
        frm.refresh_field(fieldname);
    });
}
