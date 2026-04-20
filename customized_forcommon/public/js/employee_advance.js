frappe.ui.form.on("Employee Advance", {
    refresh(frm) {
        if (frm.is_new()) {
            frm.set_value("custom_repayment_amount", 0)
        }
    },
    repay_unclaimed_amount_from_salary(frm) {
        if (frm.doc.repay_unclaimed_amount_from_salary == 0) {
            frm.set_value("custom_repayment_type", "");
            frm.set_value("custom_number_of_month", null);
            frm.set_value("custom_starting_payroll_date", "");
            frm.set_value("custom_rate", null);
            frm.clear_table("custom_next_payroll_dates");
            frm.refresh_field("custom_next_payroll_dates");
        }
    },
    custom_repayment_type(frm) {
        frm.set_value("custom_repayment_amount", 0);
        if (frm.doc.custom_repayment_type == "") {
            frm.clear_table("custom_next_payroll_dates");
            frm.refresh_field("custom_next_payroll_dates");
        }
        else if (frm.doc.custom_repayment_type == "Fixed") {
            frm.set_value("custom_number_of_month", null);
            frm.set_value("custom_rate", null);
        } else if (frm.doc.custom_repayment_type == "Number of Months") {
            frm.set_value("custom_rate", null);
        } else if (frm.doc.custom_repayment_type == "Salary Percentage") {
            frm.set_value("custom_number_of_month", null);
        }
    }
})
