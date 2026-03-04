// Copyright (c) 2025, Guba Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leave Allocation Auto Increment", {
    onload(frm) {
        // frm.trigger("get_employees");
        // Disable adding rows programmatically to the employees table when the form loads
        frm.fields_dict.employees.grid.cannot_add_rows = true;
    },
    refresh(frm) {
        // Disable adding rows programmatically to the employees table when the form loads
        frm.fields_dict.employees.grid.cannot_add_rows = true;
    },

    setup(frm) {
        frm.set_query("leave_period", function () {
            return {
                filters: {
                    is_active: 1
                }
            };
        });

        // Watch for changes in the filter_by_increment field reliably
        frm.fields_dict["filter_by_increment"].df.onchange = () => {
            frm.trigger("filter_by_increment");
        };

        // Ignore child table dirty flag to avoid "Not Saved" warning
        frm.ignore_doctypes_on_dirty_check = ["Leave Auto Increment Employees"];
    },

    date_range_based_on(frm) {
        if (frm.doc.date_range_based_on !== "Leave Period") {
            frm.set_value("leave_period", "");
            frm.refresh_field("leave_period");
        } else if (frm.doc.leave_period) {
            frm.trigger("leave_period");
        }
    },

    leave_period(frm) {
        if (frm.doc.date_range_based_on === "Leave Period" && frm.doc.leave_period) {
            frappe.call({
                method: "customized_forcommon.common_customization.doctype.leave_allocation_auto_increment.leave_allocation_auto_increment.get_leave_period",
                args: {
                    leave_period: frm.doc.leave_period
                },
                callback: function (r) {
                    if (!r.exc && r.message) {
                        let to_date = r.message.to_date;
                        frm.set_value("to_date", to_date);
                    }
                }
            });
        }
    },

    leave_type(frm) {
        if (frm.doc.leave_type) {
            frappe.call({
                method: "customized_forcommon.common_customization.doctype.leave_allocation_auto_increment.leave_allocation_auto_increment.get_total_leave_days_allocated",
                args: {
                    leave_type: frm.doc.leave_type
                },
                callback(r) {
                    if (!r.exc && r.message) {
                        let total_leave_days = r.message.total_leaves_allocated;
                        frm.set_value("max_days_of_leave_type", total_leave_days);
                    }
                }
            });
        }
    },

    filter_by_increment(frm) {
        frm.set_value("employees", []);  // Clear previous selection
        frm.trigger("get_employees");
        if (frm.doc.filter_by_increment !== "Not Allocated Before") {
            frm.set_value("leaves_to_be_allocated", "");
            frm.refresh_field("leaves_to_be_allocated");
        }
    },
    designation(frm) {
        frm.set_value("employees", []);  // Clear previous selection
        frm.trigger("get_employees");
    },

    get_employees(frm) {
        const increment_filter = frm.doc.filter_by_increment;
        console.log("Filter selected:", increment_filter);  // <-- Debug log here
        console.log("Form dirty state after update:", frm.dirty);


        frappe.call({
            method: "customized_forcommon.common_customization.doctype.leave_allocation_auto_increment.leave_allocation_auto_increment.get_filtered_employees",
            args: { increment_filter, designation: frm.doc.designation },
            callback(r) {
                if (r.message) {
                    frappe.model.with_doc(frm.doc.doctype, frm.doc.name, function () {
                        // Clear the table
                        frm.clear_table("employees");

                        // Add each employee row
                        r.message.forEach(emp => {
                            let row = frm.add_child("employees");
                            row.employee = emp.name;
                            row.employee_name = emp.employee_name;
                            row.department = emp.department;
                            row.company = emp.company;
                            row.allocation_id = emp.allocation_id || null;
                            row.from_date = emp.from_date || null;
                            row.to_date = emp.to_date || null;
                            row.leave_allocated = emp.leave_allocated || null;
                        });

                        frm.refresh_field("employees");
                    });
                }
            }

        });
    }

});
