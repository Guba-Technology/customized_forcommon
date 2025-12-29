// Copyright (c) 2025, Guba Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Warranty Request", {
    refresh(frm) {
        // Set query on the child table's employee field
        frm.fields_dict["witnesses"].grid.get_field("employee").get_query = function (doc, cdt, cdn) {
            const child = locals[cdt][cdn];
            return {
                filters: [
                    ["Employee", "name", "!=", frm.doc.employee]  // exclude parent employee
                ]
            };
        };
    },
    warranty_request_for(frm) {
        if (frm.doc.warranty_request_for == "Other Employee") {
            frm.set_value("beneficiary_company", "");
            frm.set_value("warrantee_holder", "");
            frm.set_value("address", "");
            frm.set_value("status", "");
        } else if (frm.doc.warranty_request_for == "Self") {
            frm.set_value("type_of_collateral", "");
            frm.set_value("collateral_value", "");
            frm.set_value("collateral_address", "");
            frm.set_value("employee_declaration", "");
            frm.set_value("guarantor_full_name", "");
            frm.set_value("guarantor_date_of_birth", "");
            frm.set_value("sub_city", "");
            frm.set_value("woreda", "");
            frm.set_value("kebele", "");
            frm.set_value("house_number", "");
            frm.set_value("place_of_work", "");
            frm.set_value("monthly_salary", "");
            frm.set_value("daily_income", "");
            frm.set_value("annual_income", "");
            frm.set_value("guarantor_declaration", "");
            frm.clear_table("witnesses");
            frm.set_value("guarantee_status", "");

        }

    },
    employee(frm) {
        if (frm.doc.employee) {
            frappe.db.get_value("Employee", frm.doc.employee, "designation")
                .then(r => {
                    if (!r.message || !r.message.designation) {
                        frappe.msgprint(
                            __("Designation is missing in the selected Employee record. Please update it in the Employee form.")
                        );
                    }
                });
        }
    }
});
