frappe.ui.form.on("Training Result", {
    custom_evaluation_for: function(frm) {
        const role_config = {
            "Trainee": {
                hide: ["custom_training_result_template"],
                show: ["employees"],
            },
            "Trainer": {
                hide: ["employees"],
                show: ["custom_training_result_template"],
            }
        };
        const config = role_config[frm.doc.custom_evaluation_for];
        if (config) {
      
            ["employees", "custom_training_result_template"].forEach(field => {
                frm.set_df_property(field, "hidden", false);
              
            });
            config.show.forEach(field => frm.set_df_property(field, "hidden", false));
            config.hide.forEach(field => frm.set_df_property(field, "hidden", true));

                  }
    }
});
