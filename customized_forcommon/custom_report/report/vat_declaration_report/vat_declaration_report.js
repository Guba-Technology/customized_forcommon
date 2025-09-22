frappe.query_reports["VAT Declaration Report"] = {
    "filters": [
        {
            "fieldname": "month",
            "label": "Month",
            "fieldtype": "Select",
            "options": "\n 01 \n 02 \n 03 \n 04 \n 05 \n 06 \n 07 \n 08 \n 09 \n 10 \n 11 \n 12"
        },
        {
            "fieldname": "year",
            "label": "Fiscal Year",
            "fieldtype": "Link",
            "options": "Fiscal Year"
        },
        {
            "fieldname": "vat_type",
            "label": "VAT type",
            "fieldtype": "Select",
            "options": "\nVAT\nNon VAT\n7.5 percent"
        },
       
    ],

    "formatter": function (value, row, column, data, default_formatter) {
        if (column.fieldname == "total_vat" || column.fieldname == "total_non_vat" || column.fieldname == "total_7.5_percent") {
            return flt(value, 2);
        }
        return default_formatter(value, row, column, data);
    },

   
  "onload": function(report) {
    report.page.add_inner_button("Update VAT Closing", function() {
        const year = report.get_filter_value("year");

        if (!year) {
            frappe.msgprint("Please select Fiscal Year before updating VAT closing.");
            return;
        }

        frappe.confirm(
            `Are you sure you want to update VAT Closing for fiscal year <b>${year}</b>?`,
            function() {
                // On Confirm
                frappe.call({
                    method: "customized_forcommon.custom_report.report.vat_declaration_report.vat_declaration_report.update_vat_closing",
                    args: {
                        year: year
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint("VAT Closing updated successfully.");
                        }
                    }
                });
            },
            function() {
                // On Cancel
                frappe.msgprint("VAT Closing update cancelled.");
            }
        );
    });
}


};
