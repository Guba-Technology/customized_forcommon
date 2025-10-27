// Copyright (c) 2025, Guba Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Advance Clearance", {
    refresh(frm) {
        if ((frm.doc.invoiced_amount || 0) > (frm.doc.unreturned_amount || 0)) {
            // Hide when invoiced amount is greater than unreturned_amount
            frm.set_df_property("difference_account", "hidden", 0);
            frm.set_df_property("difference_account", "reqd", 1);
        } else {
            // Show when advance <= unreturned_amount
            frm.set_df_property("difference_account", "hidden", 1);
            frm.set_df_property("difference_account", "reqd", 0);

        }
    },
    setup(frm) {

        frm.set_query("purchase_invoice", function () {
            return {
                filters: {
                    status: ["in", ["Unpaid", "Partly Paid"]],
                    docstatus: 1
                }
            }
        });
        frm.set_query("employee", function () {
            return {
                filters: {
                    status: "Active",
                    company: frm.doc.company
                }

            }
        });
        frm.set_query("employee_advance", function () {
            if (!frm.doc.employee) {
                frappe.msgprint("Please select an Employee first.");
                return {};  // returns empty query — disables options
            }

            return {
                filters: {
                    status: "Paid",
                    employee: frm.doc.employee,
                }
            }
        });

        frm.set_query("difference_account", function () {
            return {
                filters: {
                    account_type: "Payable",
                    company: frm.doc.company
                }

            }
        });
    },
    onload: function (frm) {
        if (!frm.doc.employee) {
            frm.set_value("employee_advance", null);
        }

        if ((frm.doc.invoiced_amount || 0) > (frm.doc.unreturned_amount || 0)) {
            // Hide when invoiced amount is greater than unreturned_amount
            frm.set_df_property("difference_account", "hidden", 0);
            frm.set_df_property("difference_account", "reqd", 1);
        } else {
            // Show when advance <= unreturned_amount
            frm.set_df_property("difference_account", "hidden", 1);
            frm.set_df_property("difference_account", "reqd", 0);

        }

    },
    employee: function (frm) {
        if (!frm.doc.employee_advance) {
            return;
        }
        // Check if the selected advance belongs to the new employee
        frappe.db.get_value("Employee Advance", frm.doc.employee_advance, "employee", function (r) {
            if (r && r.employee && r.employee !== frm.doc.employee) {
                frm.set_value("employee_advance", null);
                frappe.msgprint("Employee Advance has been cleared because it does not match the selected Employee.");
            }
        });
    },
});
