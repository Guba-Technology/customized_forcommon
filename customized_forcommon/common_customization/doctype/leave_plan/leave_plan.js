// Copyright (c) 2025, Guba Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Leave Plan', {
    onload: function(frm) {
        frappe.call({
            method: 'erpnext.accounts.utils.get_fiscal_year',
            args: {
                date: frappe.datetime.get_today(),
                company: frm.doc.company
            },
            callback: function(r) {
                if (r.message && r.message[0]) {
                    frm.set_value('fiscal_year', r.message[0]);
                }
            }
        });
    },
    
    // This function is triggered when the user selects a month in the first dropdown
    // It updates the second dropdown to show only the months that come after the selected month
    month1: function(frm) {
        const monthOrder = {
            "July": 1,
            "Augest": 2,
            "September": 3,
            "October": 4,
            "November": 5,
            "December": 6,
            "January": 7,
            "February": 8,
            "March": 9,
            "April": 10,
            "May": 11,
            "June": 12
        };

        const monthNames = Object.keys(monthOrder);
        const selectedIndex = monthOrder[frm.doc.month1];

        if (selectedIndex) {
            // Get months that come after the selected month
            const allowedMonths = monthNames.filter(m => monthOrder[m] > selectedIndex);
            frm.set_df_property("month2", "options", allowedMonths.join("\n"));
            frm.refresh_field("month2");
        }
    },

});
