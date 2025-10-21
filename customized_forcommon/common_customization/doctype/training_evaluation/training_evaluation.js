// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Evaluation", {
	refresh(frm) {

	},
    training_event:function(frm){
        if(frm.doc.training_event){
           frappe.call({
               method:"customized_forcommon.common_customization.doctype.training_evaluation.training_evaluation.get_training_event",
               args:{training_event:frm.doc.training_event},
               callback:function(r){
                   if(r.message){
                       frm.set_value("duration_of_training",r.message);
                       frm.refresh_field("duration_of_training");
                       
                   }
               }
           })
        }
    }
});



    
    
