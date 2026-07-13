frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        frm.dashboard.set_headline('');

        const today = frappe.datetime.get_today();
        
        if (frm.doc.contract_end_date) {
            const days_to_contract_end = frappe.datetime.get_diff(frm.doc.contract_end_date, today);
            
            if (days_to_contract_end < 0) {
                frm.dashboard.set_headline(
                    __('Attention: This employee\'s contract expired {0} days ago.', [Math.abs(days_to_contract_end)]), 
                    'red'
                );
            } else if (days_to_contract_end <= 30) {
                frm.dashboard.set_headline(
                    __('Contract ending soon: Only {0} days remaining.', [days_to_contract_end]), 
                    'orange'
                );
            }
        }

        if (frm.doc.date_of_retirement) {
            const days_to_retainment = frappe.datetime.get_diff(frm.doc.date_of_retirement, today);
            
            if (days_to_retainment >= 0 && days_to_retainment <= 15) {
                frm.dashboard.set_headline(
                    __('Retainment Review due in {0} days.', [days_to_retainment]), 
                    'blue'
                );
            }
        }
    }
});