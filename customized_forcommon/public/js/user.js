frappe.ui.form.on('User', {
    refresh: function (frm) {
        // List of modules you want to KEEP visible
        const allowed_modules = [
            "Accounts", "Stock", "Buying", "Selling", "HR", "Payroll",
            "Setup", "Core", "Custom", "Desk", "Email", "Automation",
            "Common Customization", "Contacts"
        ];

        // Target the checkboxes wrapper
        // Note: Fieldname is usually 'block_modules' in recent Frappe versions
        $('div[data-fieldname="block_modules"] .unit-checkbox').each(function () {
            let label = $(this).text().trim();

            // If the label is NOT in our allowed list, hide it
            if (!allowed_modules.includes(label)) {
                $(this).hide();
            } else {
                $(this).show(); // Ensure allowed ones are visible
            }
        });
    },
    email: function (frm) {
        const email_field = frm.fields_dict.email;

        if (frm.doc.email) {
            const email_regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (!email_regex.test(frm.doc.email)) {
                frm.set_df_property('email', 'description_html', true);
                frm.set_df_property('email', 'description', '<span style="color:red">Invalid email format.</span>');
                frm.refresh_field('email');
                return;
            }

            frappe.db.get_list('User', {
                filters: { 'email': frm.doc.email },
                fields: ['name']
            }).then(users => {
                frm.set_df_property('email', 'description_html', true);
                if (users.length && users[0].name !== frm.doc.name) {
                    frm.set_df_property('email', 'description', '<span style="color:red">This email is already used. Please choose another.</span>');
                } else {
                    frm.set_df_property('email', 'description', '');
                }
                frm.refresh_field('email');
            });
        } else {
            frm.set_df_property('email', 'description', '');
            frm.refresh_field('email');
        }
    }
});
