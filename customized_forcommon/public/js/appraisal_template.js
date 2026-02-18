frappe.ui.form.on("Appraisal Template", {
    onload: function(frm) {
        const style = document.createElement("style");
        style.innerHTML = `
            .grid-row .row-index,
            .grid-heading-row .row-index {
                display: none !important;
            }
        `;
        document.head.appendChild(style);
      
    }
    ,
    custom_criteria_for: function(frm)
    {
        const role_config = {
       "Performance Feedback": {
                show: ["rating_criteria"],
                hide: ["custom_self_appraisal_rating_criteria"],
            },
            "Self Appraisal": {
                show: ["custom_self_appraisal_rating_criteria"],
                hide: ["rating_criteria"],
            }
        };
        const config = role_config[frm.doc.custom_criteria_for];
        if (config) {
      
            ["custom_self_appraisal_rating_criteria", "rating_criteria"].forEach(field => {
                frm.set_df_property(field, "hidden", false);
              
            });
            config.show.forEach(field => frm.set_df_property(field, "hidden", false));
            config.hide.forEach(field => frm.set_df_property(field, "hidden", true));
        }
       
    }
});


