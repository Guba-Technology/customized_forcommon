// Copyright (c) 2025, Guba Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Employee Promotion', {
    onload: function(frm) {
        // Disable adding rows programmatically to the employees table when the form loads
        frm.fields_dict.employees.grid.cannot_add_rows = true;
    },

    refresh: function(frm) {
        // Diasble adding rows programmatically to the employees table when the form is refreshed
        frm.fields_dict.employees.grid.cannot_add_rows = true;

        if (
            frm.doc.docstatus === 1 &&
            frm.doc.promotion_by === "Grade" &&
            frm.doc.status === "Approved"
        ) {
            frm.add_custom_button(__('Promote by Grade'), () => {
                if (!frm.doc.new_grade) {
                    frappe.msgprint(__('Please select a new Grade before promoting.'));
                    return;
                }

                frappe.call({
                    method: "customized_forcommon.common_customization.doctype.bulk_employee_promotion.bulk_employee_promotion.promote_by_grade",
                    args: { docname: frm.doc.name },
                    callback: function(r) {
                        if (frappe._messages) frappe._messages = [];
                        if (r.message) {
                            frappe.msgprint({
                                title: __("Promotion Successful"),
                                message: __(r.message),
                                indicator: "green"
                            });
                        }
                        frm.reload_doc();
                    }
                });
            }, __("Actions"));
        } else if (
            frm.doc.docstatus === 1 &&
            frm.doc.promotion_by === "Step" &&
            frm.doc.status === "Approved"
        ) {
            frm.add_custom_button(__('Promote by Step'), () => {
                if (!frm.doc.new_step) {
                    frappe.msgprint(__('Please select a new Step before promoting.'));
                    return;
                }

                frappe.call({
                    method: "customized_forcommon.common_customization.doctype.bulk_employee_promotion.bulk_employee_promotion.promote_by_step",
                    args: { docname: frm.doc.name },
                    callback: function(r) {
                        if (frappe._messages) frappe._messages = [];
                        if (r.message) {
                            frappe.msgprint({
                                title: __("Promotion Successful"),
                                message: __(r.message),
                                indicator: "green"
                            });
                        }
                        frm.reload_doc();
                    }
                });
            }, __("Actions"));
        }
    },
    current_grade: function(frm) {
        if (!frm.doc.current_grade && !frm.doc.current_step) {
            frm.clear_table("employees");
            frm.refresh_field("employees");
            return;
        }
        populate_employee_table(frm);
    },
    current_step: function(frm) {
        if (!frm.doc.current_grade && !frm.doc.current_step) {
            frm.clear_table("employees");
            frm.refresh_field("employees");
            return;
        }
        populate_employee_table(frm);
    }
});

function populate_employee_table(frm) {
    const grade = frm.doc.current_grade;
    const step = frm.doc.current_step;

    if (!grade && !step) return;

    frm.clear_table("employees");
    frm.refresh_field("employees");

    frappe.call({
        method: "customized_forcommon.common_customization.doctype.bulk_employee_promotion.bulk_employee_promotion.get_employees_by_grade_or_step",
        args: { grade, step },
        freeze: true,
        freeze_message: __("Fetching Employees..."),
        callback: function(r) {
            if (r.message && r.message.length) {
                r.message.forEach(emp => {
                    frm.add_child("employees", {
                        employee: emp.name,
                        employee_name: emp.full_name,
                        dept: emp.department,
                        designation: emp.designation,
                        grade: emp.grade,
                        step: emp.custom_step
                    });
                });
                frm.refresh_field("employees");
            } else {
                frappe.msgprint({
                    title: __("No Employees Found"),
                    message: __("No active employees found with the selected Grade and/or Step."),
                    indicator: "red"
                });
            }
        }
    });
}
