// Ensure this matches your specific python function for ALL employees
const SYNC_ALL_METHOD = "customized_forcommon.common_customization.doctype.attendance_collection.attendance_collection.sync_attendance_to_collection_for_all_employees";

frappe.listview_settings['Attendance Collection'] = {
    onload: function(listview) {
        
        listview.page.add_inner_button(__('Fetch All Attendance'), function() {
            frappe.confirm(__('Are you sure you want to sync attendance for ALL active employees?'), () => {
                frappe.call({
                    method: SYNC_ALL_METHOD,
                    freeze: true,
                    freeze_message: __("Processing all employees..."),
                    callback: function(r) {
                        if (r.message) {
                            listview.refresh();
                            frappe.show_alert({ 
                                message: __("Full Employee sync complete"), 
                                indicator: 'blue' 
                            });
                        }
                    }
                });
            });
        });
    }
};