//public/js/employee_referal_custom.js
frappe.ui.form.on('Employee Referral', {
    onload:function(frm) {
       if (frm.doc.custom_is_referrer_outsider_employee) {
            frm.set_df_property('custom_referrer_full_name', 'hidden', 0);
            frm.set_df_property('referrer', 'reqd', 0);
            frm.set_df_property('referrer', 'hidden', 1);
        }
            else {
            frm.set_df_property('custom_referrer_full_name', 'hidden', 1);
            frm.set_df_property('referrer', 'reqd', 1);
            frm.set_df_property('referrer', 'hidden', 0);
        }
    },
    custom_is_referrer_outsider_employee:function(frm) {
        if (frm.doc.custom_is_referrer_outsider_employee) {
            frm.set_df_property('custom_referrer_full_name', 'hidden', 0);
            frm.set_df_property('referrer', 'reqd', 0);
            frm.set_df_property('referrer', 'hidden', 1);
            frm.set_value('referrer', '');
        }
            else {
            frm.set_df_property('custom_referrer_full_name', 'hidden', 1);
            frm.set_df_property('referrer', 'reqd', 1);
            frm.set_df_property('referrer', 'hidden', 0);
                frm.set_value('custom_referrer_full_name', '');
        }
    },

});