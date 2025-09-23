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
  
   
    frappe.db.get_list("Fiscal Year", {
        fields: ["name", "year_end_date"], 
        limit: 1,
        order_by: "creation desc" // or use filters to get the active year
    }).then(fiscal_years => {
        if (!fiscal_years.length) return;

        const fiscal_year = fiscal_years[0];
        const end_date = frappe.datetime.str_to_obj(fiscal_year.year_end_date);
        const today = frappe.datetime.str_to_obj(frappe.datetime.get_today());
        const days_remaining = frappe.datetime.get_diff(end_date, today);

        // Show button only if within 30 days before fiscal year end
        if (days_remaining <= 30 && days_remaining >= 0) {
            const btn = report.page.add_inner_button(`Update VAT Closing (${days_remaining} days left)`, function() {
                frappe.confirm(
                    `Are you sure you want to update VAT Closing for fiscal year <b>${fiscal_year.name}</b>?`,
                    function() {
                        frappe.call({
                            method: "customized_forcommon.custom_report.report.vat_declaration_report.vat_declaration_report.update_vat_closing",
                            args: { year: fiscal_year.name },
                            callback: function(r) {
                                if (r.message) {
                                    frappe.msgprint("VAT Closing updated successfully.");
                                }
                            }
                        });
                    },
                    function() {
                        frappe.msgprint("VAT Closing update cancelled.");
                    }
                );
            });
            $(btn).removeClass("btn-default").addClass("btn btn-success");
        }
       else{
          if (days_remaining < 0) {
       const btn = report.page.add_inner_button(` 📌 Fiscal year ended ${Math.abs(days_remaining)} days ago. VAT closing is locked.`,);
       $(btn).removeClass("btn-default").addClass("btn-info");
        }
        else if(days_remaining > 30 && days_remaining <= 60){
            const btn = report.page.add_inner_button(` ⏳ VAT closing will be available in ${Math.abs(days_remaining)} days`,);
            $(btn).removeClass("btn-default").addClass("btn-danger");   
        }
        else{
            const btn = report.page.add_inner_button(`FISCAL YEAR: ${fiscal_year.name}`,);
            $(btn).removeClass("btn-default").addClass("btn-info");
        }

       }
    });
}};
