frappe.ui.form.on("Training Report", {
    setup: function(frm) {
           data_fetcher(frm); 
        }
        
    ,
    training_event:function(frm)
    {
        data_fetcher(frm);
    },
  onload: function(frm) {
  frm.set_df_property("employee", "read_only", 1);

}

});

function data_fetcher(frm)
{

    
    if (frm.doc.training_event == "" || frm.doc.training_event == null) {
            frm.set_df_property("employee", "read_only", 1);
            return;
        }
        else{
            frm.set_df_property("employee", "read_only", 0);

    frappe.call({
            method: "customized_forcommon.common_customization.doctype.training_report.training_report.get_employee_list",
            args:{training_event: frm.doc.training_event},
            callback: function(r) {
                if (!r.exc && r.message) {
                    const employee_list = r.message;
                    frm.set_query("employee", function() {
                        return {
                            filters: {
                                name: ["in", employee_list]
                            }
                        };
                    });
                }
            }
        });
}

}
