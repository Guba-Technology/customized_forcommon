console.log("Custom Bank Reconciliation JS loaded!");

frappe.query_reports["Bank Reconciliation Statement"] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            reqd: 1,
            default: frappe.defaults.get_user_default("Company"),
        },
        {
            fieldname: "account",
            label: __("Bank Account"),
            fieldtype: "Link",
            options: "Account",
            reqd: 1,
        },
        {
            fieldname: "report_date",
            label: __("Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1,
        },
    ],

    formatter: function (value, row, column, data, default_formatter) {
        if (data && data.is_summary_row) {
            // Use default formatter so currency/number formatting works
            return default_formatter(value, row, column, data);
        }
        return default_formatter(value, row, column, data);
    },
};