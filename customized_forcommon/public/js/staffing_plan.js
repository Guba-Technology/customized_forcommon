frappe.ui.form.on("Staffing Plan", {
    setup: function (frm) {
        frm.set_query("designation", "staffing_details", function () {
            let designations = [];
            (frm.doc.staffing_details || []).forEach(function (row) {
                if (row.designation) {
                    designations.push(row.designation);
                }
            });
            return {
                filters: [["Designation", "name", "not in", designations]],
            };
        });

        frm.set_query("department", function () {
            return {
                filters: {
                    company: frm.doc.company,
                },
            };
        });
    }
});
