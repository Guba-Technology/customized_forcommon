frappe.ui.form.on("Bulk Employee Transfer", {
    onload: function(frm) {
        frm.set_query("property", function() {
            return {
                filters: [
                    ["DocType", "name", "in", [
                        "Company", 
                        "Designation", 
                        "Branch", 
                        "Department", 
                        "Employee Grade", 
                        "Employee Step"
                    ]]
                ]
            };
        });
        frm.set_df_property("property", "only_select", 1);
        if (!frm.doc.property) {
            frm.set_value("property", "Company");
        }
    },

    property: function(frm) {
        const selected_prop = frm.doc.property;
        if (!selected_prop) return;

        const target_fields = ["old_value", "new_value"];
        target_fields.forEach(field => {
            let prefix = (field === "old_value") ? __("Current") : __("New");
            frm.set_df_property(field, "label", `${prefix} ${__(selected_prop)}`);
            frm.set_value(field, "");
        });
        frm.refresh_fields();
    },

    old_value: function(frm) {
        const selected_doctype = frm.doc.property;
        const filter_val = frm.doc.old_value;

        if (!selected_doctype || !filter_val) {
            frm.clear_table("employee_list");
            frm.refresh_field("employee_list");
            return;
        }

        const doctype_to_field_map = {
            "Company": "company",
            "Designation": "designation",
            "Branch": "branch",
            "Department": "department",
            "Employee Grade": "grade",
            "Employee Step": "custom_step" 
        };

        const db_fieldname = doctype_to_field_map[selected_doctype];

        if (!db_fieldname) return;

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Employee",
                filters: {
                    "status": "Active",
                    [db_fieldname]: filter_val
                },
                fields: ["name", "employee_name", "department", "designation", "grade", "branch"],
                limit_page_length: 500
            },
            callback: function(r) {
                frm.clear_table("employee_list");
                if (r.message && r.message.length > 0) {
                    r.message.forEach(emp => {
                        let row = frm.add_child("employee_list");
                        row.employee = emp.name;
                        row.full_name = emp.employee_name;
                        row.dept = emp.department;
                        row.designation = emp.designation;
                        row.grade = emp.grade;
                        row.branch = emp.branch;
                    });
                    
                    frappe.show_alert({
                        message: __("Found {0} Employee{1}", [r.message.length, r.message.length > 1 ? "s" : ""]),
                        indicator: 'green'
                    });
                }
                frm.refresh_field("employee_list");
            }
        });
    }
});