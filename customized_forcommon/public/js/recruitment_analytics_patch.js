// Ensure we don't overwrite if someone else patched it
$(document).on('app_ready', function() {

    console.log("Custom patch for Recruitment Analytics loaded");
    // We hook into the report rendering process
    const original_report = frappe.query_reports["Recruitment Analytics"];

    // If it's already loaded, patch it now
    if (original_report) {
        add_custom_filters(original_report);
    } 

    // The most reliable way: redefine the object so that 
    // when Frappe looks for it, it finds your version.
    Object.defineProperty(frappe.query_reports, "Recruitment Analytics", {
        get: function() {
            return this._recruitment_analytics;
        },
        set: function(val) {
            if (val && val.filters && !val._patched) {
                val.filters.push({
                    fieldname: "from_date",
                    label: __("From Date"),
                    fieldtype: "Date",
                    default: frappe.datetime.month_start(),
                });
                val.filters.push({
                    fieldname: "to_date",
                    label: __("To Date"),
                    fieldtype: "Date",
                    default: frappe.datetime.now_date(),
                });
                val._patched = true;
            }
            this._recruitment_analytics = val;
        },
        configurable: true
    });
});