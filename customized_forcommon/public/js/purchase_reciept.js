frappe.ui.form.on("Purchase Receipt", {
    onload: function(frm) {
        console.log("Purchase Receipt form loaded");
        frm.set_df_property("set_warehouse", "reqd", 1);
    }    
})