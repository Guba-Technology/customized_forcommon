frappe.ui.form.on("Sales Invoice", {
    validate: function(frm) {
        let tax_type = frm.doc.taxes.map(tax => tax.account_head || "");

        if (tax_type.some(t => t.toLowerCase().includes("vat")) || tax_type.some(t => t.toLowerCase().match("/vat\w*/"))) 
            {
          frm.set_df_property("custom_vat_category", "reqd", true);
            frm.set_df_property("custom_type_of_sale", "reqd", true);
            frm.set_df_property("custom_mrc_number", "reqd", true);
            frm.set_df_property("custom_vat_receipt_number", "reqd", true);
            frm.set_df_property("custom_description", "reqd", true);
        } else {
            frm.set_df_property("custom_vat_category", "reqd", false);
            frm.set_df_property("custom_type_of_sale", "reqd", false);
            frm.set_df_property("custom_mrc_number", "reqd", false);
            frm.set_df_property("custom_vat_receipt_number", "reqd", false);
            frm.set_df_property("custom_description", "reqd", false);
        }
        if (tax_type.some(t => t.toLowerCase().includes("withholding")) || tax_type.some(t => t.toLowerCase().match("/withhold\w*/")))
        {
           frm.set_df_property("custom_receipt_number", "reqd", true);
            frm.set_df_property("custom_withhold_date", "reqd", true);
        } else {
            frm.set_df_property("custom_receipt_number", "reqd", false);
            frm.set_df_property("custom_withhold_date", "reqd", false);
        }
    }
});
