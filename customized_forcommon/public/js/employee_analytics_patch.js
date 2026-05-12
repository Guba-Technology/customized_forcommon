//public/js/employe_analytics_patch.js
$(document).on('app_ready', function() {
    Object.defineProperty(frappe.query_reports, "Employee Analytics", {
        get: function() {
            return this._employee_analytics;
        },
        set: function(val) {
            if (val && val.filters && !val._patched) {
                const param_filter = val.filters.find(f => f.fieldname === "parameter");
                if (param_filter && !param_filter.options.includes("Exit Employee")) {
                    param_filter.options.push("Exit Employee");
                }
                val._patched = true;
            }
            this._employee_analytics = val;
        },
        configurable: true
    });
});