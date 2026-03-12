// custom_purchase_order_analysis.js
frappe.query_reports["Purchase Order Analysis"] = {
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
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.defaults.get_user_default("year_start_date"),
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.defaults.get_user_default("year_end_date"),
        },
        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "MultiSelectList",
            options: [
                { value: "To Bill", label: __("To Bill") },
                { value: "To Receive", label: __("To Receive") },
                { value: "To Receive and Bill", label: __("To Receive and Bill") },
                { value: "Completed", label: __("Completed") },
            ],
        },
        {
            fieldname: "name",
            label: __("Purchase Order"),
            fieldtype: "MultiSelectList",
            options: "Purchase Order",
            get_data: function (txt) {
                return frappe.db.get_link_options("Purchase Order", txt);
            },
        },
        {
            fieldname: "project",
            label: __("Project"),
            fieldtype: "MultiSelectList",
            options: "Project",
            get_data: function (txt) {
                return frappe.db.get_link_options("Project", txt);
            },
        },
        {
            fieldname: "group_by_po",
            label: __("Group by Purchase Order"),
            fieldtype: "Check",
            default: 0,
        },
        // Add custom purchase type filter
        {
            fieldname: "custom_purchase_type",
            label: __("Purchase Type"),
            fieldtype: "Select",
            options: "\nLocal\nForeign",
        },
    ],

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname == "pending_qty" && data && data.pending_qty > 0) {
            value = "<span style='color:red'>" + value + "</span>";
        } else if (column.fieldname == "pending_amount" && data && data.pending_amount > 0) {
            value = "<span style='color:red'>" + value + "</span>";
        }
        return value;
    },
};