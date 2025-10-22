// Copyright (c) 2025, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("Student Report", {
    setup: function(frm) {
        frappe.db.get_list("Training Commitment", {
            fields: ["employee"],
         
        }).then(records => {
            const employee_list = records.map(r => r.employee);
            frm.set_query("employee", function() {
                return {
                    filters: {
                        name: ["in", employee_list] // 'name' is the field in Employee
                    }
                };
            });
        });
    }
});

