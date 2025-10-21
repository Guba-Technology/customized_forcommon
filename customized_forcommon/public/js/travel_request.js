frappe.ui.form.on("Travel Request", {
    onload(frm) {
        let existing_options = frm.fields_dict.travel_type.df.options || "";
        let additional_options = ["Domestic", "International",  "Field Work"];
        let merged_options = [...new Set(existing_options.split("\n").concat(additional_options))];
        frm.set_df_property("travel_type", "options", merged_options.join("\n"));
    }});
    frappe.ui.form.on("Employee Grievance", {
    raised_by:function(frm){
       if (frm.doc.raised_by) {
        frappe.call({
        method:"hrms.hr.doctype.training_evaluation.training_evaluation.grievance_auto_complete",
        args:{raised_by:frm.doc.raised_by},
        callback:function(r){
            if(r.message){
                frm.set_value("custom_grade",r.message.grade);
                frm.refresh_field("duration_of_training");
                frm.set_value("custom_company", r.message.company)
                frm.refresh_field("custom_company")
                frm.set_value("custom_address", r.message.address)
                frm.refresh_field("custom_address")
                
            }
        }
    }) 
    }
    else{
        frm.set_value("custom_grade",null)
        frm.refresh_field("custom_grade")
        frm.set_value("custom_company", null)
        frm.refresh_field("custom_company")
        frm.set_value("custom_address", null)
        frm.refresh_field("custom_address")
    }
}
    })
