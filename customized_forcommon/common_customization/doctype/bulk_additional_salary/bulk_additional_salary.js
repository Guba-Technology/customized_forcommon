frappe.ui.form.on("Bulk Additional Salary", {
    onload: function (frm) {
        // Disable adding rows programmatically to the employees table when the form loads
        frm.fields_dict.employees.grid.cannot_add_rows = true;
    },
    refresh(frm) {
        if (frm.doc.filtered_by === "All") {
            frm.set_value("value", "");
        }
        if (!frm.is_new()) return;
        clear_employees(frm);
        load_employees(frm);
    },
    company(frm) {
        clear_employees(frm);
        load_employees(frm);
    },

    filtered_by(frm) {
        frm.set_value("value", "");
        if (frm.doc.filtered_by) {
            let filter = frm.doc.filtered_by;
            frm.set_df_property("value", "label", `Select ${filter}`);
        }
        clear_employees(frm);
        load_employees(frm);
    },
    value(frm) {
        clear_employees(frm);
        load_employees(frm);
    },
    salary_type(frm) {
        if (frm.doc.salary_type == "Common") {
            frm.set_value("amount", 0)
        } else {
            frm.set_value("rate", 0)
        }
    }
});
function clear_employees(frm) {
    frm.clear_table("employees");
    frm.refresh_field("employees");
}
function load_employees(frm) {

    frappe.call({
        method: "customized_forcommon.common_customization.doctype.bulk_additional_salary.bulk_additional_salary.get_filtered_employees",
        args: {
            company: frm.doc.company,
            filtered_by: frm.doc.filtered_by,
            value: frm.doc.value
        },
        callback: function (r) {

            if (!r.message) return;

            frm.clear_table("employees");

            r.message.forEach(emp => {

                let row = frm.add_child("employees");

                row.employee = emp.name;
                row.employee_name = emp.employee_name;
                row.amount = 0;

            });

            frm.refresh_field("employees");
        }
    });

}