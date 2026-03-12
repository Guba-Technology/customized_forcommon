const METHOD_PATH = "customized_forcommon.common_customization.doctype.attendance_collection.attendance_collection.sync_attendance_to_collection_bulk";

frappe.ui.form.on("Attendance Collection", {
    onload: function(frm) {
        frm.trigger('filter_paid_rows');
        frm.set_df_property("days_to_be_deducted", "read_only", 1);
        frm.set_df_property("hours_to_be_deducted", "read_only", 1);

    },

    refresh: function(frm) {
        frm.trigger('filter_paid_rows');
        if (window.attendance_monitor) clearInterval(window.attendance_monitor);

        window.attendance_monitor = setInterval(() => {
            if (frm.fields_dict.employee_checkin_list && frm.fields_dict.employee_checkin_list.grid) {
                let current_selection = frm.fields_dict.employee_checkin_list.grid.get_selected() || [];
                
                if (current_selection.length !== (frm.last_selection_count || 0)) {
                    frm.last_selection_count = current_selection.length;
                    frm.trigger('calculate_from_system_selection');
                }
            }
        }, 300);

        if (frm.doc.employee) {
            frm.add_custom_button(__('Fetch Attendance Data'), () => {
                execute_sync([frm.doc.employee], () => frm.reload_doc());
            }, __("Actions"));
        }

        frm.trigger('calculate_from_system_selection');
    },

    filter_paid_rows: function(frm) {
        frm.set_query("employee_checkin_list", () => {
            return { filters: { "status": ["!=", "Paid"] } };
        });
        
        frm.fields_dict.employee_checkin_list.grid.get_field("status").get_query = function() {
            return { filters: { "status": ["!=", "Paid"] } };
        };
        
        frm.doc.employee_checkin_list = (frm.doc.employee_checkin_list || []).filter(row => row.status !== "Paid");
        frm.refresh_field("employee_checkin_list");
    },

    utilize_it_on: function(frm) {
        frm.trigger('calculate_from_system_selection');
    },

    on_unload: function() {
        if (window.attendance_monitor) clearInterval(window.attendance_monitor);
    },

    employee_checkin_list_on_form_render: function(frm) {
        frm.trigger('calculate_from_system_selection');
    },

    calculate_from_system_selection: function(frm) {
        let grid = frm.fields_dict.employee_checkin_list.grid;
        let selected_row_names = grid ? grid.get_selected() : [];
        
        let unique_dates = new Set();
        let total_minutes = 0;

        (frm.doc.employee_checkin_list || []).forEach(row => {
            if (selected_row_names.includes(row.name) && row.status !== "Paid") {
                if (row.attendance_date) {
                    unique_dates.add(row.attendance_date);
                }

                let start = row.inn; 
                if (start && row.out) {
                    total_minutes += frappe.datetime.get_minute_diff(row.out, start);
                }
            }
        });

        frm.set_value("total_days", unique_dates.size);
        frm.set_value("days_to_be_deducted", unique_dates.size);
        frm.set_value("hours_to_be_deducted", total_minutes / 60);
        frm.set_value("total_hours", total_minutes / 60);

        let is_active = selected_row_names.length > 0 || unique_dates.size > 0;
        const fields = ["total_days", "total_hours", "utilize_it_on", "days_to_be_deducted", "hours_to_be_deducted", "section_break_deductibles"];
        fields.forEach(f => frm.set_df_property(f, "hidden", is_active ? 0 : 1));

        handle_dynamic_buttons(frm, selected_row_names);
    }
});

function handle_dynamic_buttons(frm, selected_rows) {
    frm.remove_custom_button(__('Process Overtime'));
    frm.remove_custom_button(__('Process Compensatory Leave'));

    if (!selected_rows || selected_rows.length === 0) return;

    if (frm.doc.utilize_it_on === "Overtime") {
        frm.add_custom_button(__('Process Overtime'), () => {
            run_process_call(frm, selected_rows, "process_overtime_request", "Overtime Request");
        }).addClass('btn-primary');
    } 
    else if (frm.doc.utilize_it_on === "Compensatory Leave") {
        frm.add_custom_button(__('Process Compensatory Leave'), () => {
            run_process_call(frm, selected_rows, "process_compensatory_leave_request", "Compensatory Leave");
        }).addClass('btn-primary');
    }
}

function run_process_call(frm, rows, method_name, label) {
    frm.save().then(() => {
        frappe.call({
            method: `customized_forcommon.common_customization.doctype.attendance_collection.attendance_collection.${method_name}`,
            args: {
                docname: frm.doc.name,
                selected_rows: rows
            },
            freeze: true,
            freeze_message: __(`Generating ${label}...`),
            callback: function(r) {
                if (r.message) {
                    frappe.show_alert({ message: __(`${label} Created: ${r.message}`), indicator: 'green' });
                    frm.reload_doc();
                }
            }
        });
    });
}

function execute_sync(employee_ids, callback) {
    frappe.call({
        method: METHOD_PATH,
        args: { employee_ids: employee_ids },
        freeze: true,
        freeze_message: __("Updating collections..."),
        callback: function(r) {
            if (r.message) {
                if(callback) callback();
                frappe.show_alert({ message: __("Sync Complete"), indicator: 'green' });
            }
        }
    });
}