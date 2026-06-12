frappe.ui.form.on('Leave Application', {
    leave_type: function (frm) {
        calculate_as_of_today(frm);
    },
    from_date: function (frm) {
        calculate_as_of_today(frm);
    }
});

function calculate_as_of_today(frm) {
    if (!frm.doc.leave_type || !frm.doc.employee) return;

    frappe.call({
        method: "customized_forcommon.api.calculate_as_of_today_balance",
        args: {
            employee: frm.doc.employee,
            leave_type: frm.doc.leave_type
        },
        callback: function (r) {
            if (r.message !== undefined) {
                frm.set_value("custom_as_of_today", r.message);
            }
        }
    });
}