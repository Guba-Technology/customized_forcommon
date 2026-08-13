frappe.ui.form.on('Workstation', {
    onload: function(frm) {
        // Hide standard fixed-cost fields
        frm.set_df_property('hour_rate_electricity', 'hidden', 1);
        frm.set_df_property('hour_rate_rent', 'hidden', 1);
        frm.set_df_property('hour_rate_consumable', 'hidden', 1);
        frm.set_df_property('hour_rate_labour', 'hidden', 1);
    },
    validate: function(frm) {
        calculate_hour_rate(frm);
    }
});

frappe.ui.form.on('Cost Components', {
    operating_cost: function(frm, cdt, cdn) {
        calculate_hour_rate(frm);
    },
    custom_cost_components_remove: function(frm, cdt, cdn) {
        calculate_hour_rate(frm);
    }
});

function calculate_hour_rate(frm) {
    let total_cost = 0.0;
    
    if (frm.doc.custom_cost_components && frm.doc.custom_cost_components.length > 0) {
        frm.doc.custom_cost_components.forEach(row => {
            total_cost += flt(row.operating_cost);
        });
    }
    
    frm.set_value('hour_rate', total_cost);
}