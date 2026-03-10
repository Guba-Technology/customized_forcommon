frappe.ui.form.on('Quotation', {
    onload: function (frm) {
       frm.set_df_property('custom_reference_no', 'read_only', 1);
       frm.set_df_property('custom_reference_no','hidden', 1);
    //    now_date = frappe.datetime.get_today();
       // add 5 or 8 days to now_date
       // valid_till_date = frappe.datetime.add_days(now_date, 5);
       
       frappe.call({
          method: "frappe.client.get_value",
          args: {
                doctype:"Selling Settings",
                fieldname:"custom_quotation_valid_date",
          },
          callback: function(r) {
             if (r.message.custom_quotation_valid_date) {
                valid_till_date = r.message.custom_quotation_valid_date;
                if (valid_till_date == 0 || valid_till_date == null) {
                    valid_till_date = 5;
                }
            frm.set_value("valid_till", frappe.datetime.add_days(frappe.datetime.get_today(), valid_till_date));
            frm.set_df_property("valid_till", "read_only", 1);
            frm.refresh_field("valid_till"); 
            }
            else {
                valid_till_date = frappe.datetime.add_days(now_date, 5);
                frm.set_value("valid_till", valid_till_date);
                frm.set_df_property("valid_till", "read_only", 1);
                frm.refresh_field("valid_till"); 
            }
          }
       });
       
    },
})