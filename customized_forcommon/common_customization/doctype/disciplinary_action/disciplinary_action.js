// Copyright (c) 2025, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("Disciplinary Action", {
    employee_grievance: function (frm) {
        if (frm.doc.employee_grievance) {
            frappe.call({
                method:"frappe.client.get",
                args: {
                    doctype: "Employee Grievance",
                    name: frm.doc.employee_grievance
                },
                callback: function (r) {
                    frm.set_value("employee", r.message.raised_by);
                }
            })
        }
        
    }
});
