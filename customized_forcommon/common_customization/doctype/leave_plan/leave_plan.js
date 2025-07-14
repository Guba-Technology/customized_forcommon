frappe.ui.form.on('Leave Plan', {
    onload: function(frm) {
        // Set fiscal year
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

        const monthOrder = get_month_order();
        const monthNames = Object.keys(monthOrder);

        // If month1 is set, filter month2
        if (frm.doc.month1) {
            const index1 = monthOrder[frm.doc.month1];
            const allowedMonth2 = [''].concat(
                monthNames.filter(m => monthOrder[m] > index1)
            );
            frm.set_df_property("month2", "options", allowedMonth2.join("\n"));

            // Handle month3 based on month2 or month1
            let baseIndex = frm.doc.month2
                ? monthOrder[frm.doc.month2]
                : index1;
            const allowedMonth3 = [''].concat(
                monthNames.filter(m => monthOrder[m] > baseIndex)
            );
            frm.set_df_property("month3", "options", allowedMonth3.join("\n"));
        }

        frm.refresh_fields(["month2", "month3"]);
    },

    month1: function(frm) {
        const monthOrder = get_month_order();
        const monthNames = Object.keys(monthOrder);
        const selectedIndex = monthOrder[frm.doc.month1];

        if (selectedIndex) {
            frm.set_value('month2', '');
            frm.set_value('month3', '');

            const allowedMonths2 = [''].concat(
                monthNames.filter(m => monthOrder[m] > selectedIndex)
            );

            frm.set_df_property("month2", "options", allowedMonths2.join("\n"));
            frm.set_df_property("month3", "options", '');
            frm.refresh_fields(["month2", "month3"]);
        }
    },

    month2: function(frm) {
        const monthOrder = get_month_order();
        const monthNames = Object.keys(monthOrder);

        const index1 = monthOrder[frm.doc.month1];
        const index2 = monthOrder[frm.doc.month2];

        frm.set_value('month3', '');

        // If month2 is selected, base month3 on that
        let baseIndex = index2 || index1;

        const allowedMonths3 = [''].concat(
            monthNames.filter(m => monthOrder[m] > baseIndex)
        );

        frm.set_df_property("month3", "options", allowedMonths3.join("\n"));
        frm.refresh_field("month3");
    }
});

function get_month_order() {
    return {
        "July": 1,
        "August": 2,
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
}
