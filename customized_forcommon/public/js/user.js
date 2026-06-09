frappe.ui.form.on('User', {
    validate: function (frm) {
        if (frm.doc.birth_date) {
            const today = frappe.datetime.get_today();
            if (frm.doc.birth_date > today) {
                frappe.throw(__('Birth Date cannot be in the future'));
            }

            const birthYear = frappe.datetime.str_to_obj(frm.doc.birth_date).getFullYear();
            const thisYear = new Date().getFullYear();
            if (thisYear - birthYear < 18) {
                frappe.throw(__('User must be at least 18 years old'));
            }
        }
    },
    refresh: function (frm) {
        // Set Time Zone to Read Only and Set Value
        frm.set_value('time_zone', 'Africa/Addis_Ababa');
        frm.set_df_property('time_zone', 'read_only', 1);
        frm.set_df_property("app_section", "hidden", 1);
        frm.set_df_property("third_party_authentication", "hidden", 1);

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