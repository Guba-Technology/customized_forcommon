frappe.ui.form.on('Employee', {

    onload: function(frm) {
        frm.set_df_property("gender", "only_select", 1);
    },

    // Triggered whenever personal_email or company_email changes
    personal_email: function(frm) {
        validate_email_field(frm, 'personal_email');
    },

    company_email: function(frm) {
        validate_email_field(frm, 'company_email');
    },
     onload_post_render(frm) {
        const dob_field = frm.fields_dict.date_of_birth?.$input;
        if (!dob_field) return;

        if (dob_field.hasClass('hasDatepicker')) {
            dob_field.datepicker('destroy');
        }

        // Set dynamic maxDate: today minus X years
        const today = new Date();
        const age_limit = 18; 
        const max_dob = new Date();
        max_dob.setFullYear(today.getFullYear() - age_limit);

        // Initialize datepicker
        dob_field.datepicker({
            changeYear: true,
            changeMonth: true,
            maxDate: max_dob, // today minus X years
            yearRange: `1900:${max_dob.getFullYear()}` //limit year dropdown
        });
    },

    before_save(frm) {
        if (frm.doc.date_of_birth) {
            const dob = frappe.datetime.str_to_obj(frm.doc.date_of_birth);
            const today = new Date();
            const age_limit = 18; 
            const max_dob = new Date();
            max_dob.setFullYear(today.getFullYear() - age_limit);

            if (dob > max_dob) {
                frappe.msgprint(
                    `Age must be above 18 years old, cannot be after ${frappe.datetime.obj_to_str(max_dob)}`
                );
                frappe.validated = false;
            }
        }
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
