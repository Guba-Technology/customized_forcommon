frappe.ui.form.on("Sales Invoice", {
    validate: function(frm) {
        validate_all(frm);
        
    }
});
frappe.ui.form.on("Purchase Invoice", {
    validate: function(frm) {
        // let tax_type = frm.doc.taxes.map(tax => tax.account_head || "");
       validate_all(frm);
      
    },

  
});
frappe.ui.form.on('Company', {
    onload: function(frm) {
        if (window.location.hash === "#vat_account") {
            frm.page.tabs.forEach(tab => {
                if (tab.label && tab.label.toLowerCase().includes("vat")) {
                    frm.page.show_tab(tab.label);
                }
            });
        }
    }
});






function validate_all(frm)
{
     let tax_type = frm.doc.taxes
    .map(tax => tax.account_head)
    .filter(head => head); 
// console.log("Filtered Tax Type List:", tax_type);
      
        frappe.call({
          method:
            "customized_forcommon.custom_report.my_utilities.data_validator.validate_tax_type",
          args: {
            taxes: tax_type,
          },
          callback: function (r) {
            if (!r.exec && r.message) {

            //   if (r.message.vat) {
            //     set_mandatory(frm,"vat");
            //   } else {
            //     set_free(frm,"vat");
            //   }
            //   if (r.message.withhold) {
            //     set_mandatory(frm, "withhold");
            //   } else {
            //     set_free(frm, "withold");
            //   }
              if(r.message.vat_not_exist){
                
         frappe.show_alert({
              message: `
                <b style="color:red">⚠️ Unregistered VAT Account detected</b><br>
                Please enter a valid VAT Account.<br>
                You can set the account in the 
                <a href="/app/company/${encodeURIComponent(frm.doc.company)}" target="_blank">
                  ${frm.doc.company}'s VAT Account Tab
                </a>.
              `,
              indicator: 'red'
            });





                
              }
              if (r.message.wh_not_exist){
                // frm.set_value("custom_receipt_number", null);
                // frm.refresh_field("custom_receipt_number");
                // set_mandatory(frm, "withhold");
                frappe.show_alert({
                  message: `
                    <b style="color:red">⚠️ Unregistered Withhold Account detected</b><br>
                    Please enter a valid Withhold Account.<br>
                    You can set the account in the 
                    <a href="/app/company/${encodeURIComponent(frm.doc.company)}" target="_blank">
                      ${frm.doc.company}'s VAT Account Tab
                    </a>.
                  `,
                  indicator: 'red'
                });


              }
             
            }
          },
        });
        
    }





function set_mandatory(frm, element){
if (element == "vat")
{
            frm.set_df_property("custom_vat_category", "reqd", true);
            frm.set_df_property("custom_type_of_sale", "reqd", true);
            frm.set_df_property("custom_mrc_number", "reqd", true);
            frm.set_df_property("custom_vat_receipt_number", "reqd", true);
            frm.set_df_property("custom_description", "reqd", true);
}
if (element == "withhold")
{
            frm.set_df_property("custom_receipt_number", "reqd", true);
            frm.set_df_property("custom_withhold_date", "reqd", true);
}

}
function set_free(frm, element)
{
    if (element == "vat")
    {
            frm.set_df_property("custom_vat_category", "reqd", false);
            frm.set_df_property("custom_type_of_sale", "reqd", false);
            frm.set_df_property("custom_mrc_number", "reqd", false);
            frm.set_df_property("custom_vat_receipt_number", "reqd", false);
            frm.set_df_property("custom_description", "reqd", false);
    }
    if (element == "withhold")
    {
            frm.set_df_property("custom_receipt_number", "reqd", false);
            frm.set_df_property("custom_withhold_date", "reqd", false);
    }
}
