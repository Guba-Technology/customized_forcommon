const METHOD_PATH = "customized_forcommon.common_customization.doctype.attendance_collection.attendance_collection.sync_attendance_to_collection_bulk";

frappe.ui.form.on("Attendance Collection", {
    onload: function(frm) {
        frm.trigger('filter_paid_rows');
        populate_processed_employee_attendance_list(frm);
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

  calculate_from_system_selection: async function(frm) {
    const grid = frm.fields_dict.employee_checkin_list.grid;
    const selected_row_names = grid ? grid.get_selected() : [];
    
    const working_hours = flt(await frappe.db.get_single_value("HR Settings", "standard_working_hours")) || 8;
    const mins_per_day = working_hours * 60;

    let total_seconds = 0;
    let missing_punch_days = 0;
    let has_selection = selected_row_names.length > 0;

    (frm.doc.employee_checkin_list || []).forEach(row => {
        if (selected_row_names.includes(row.name) && row.status !== "Paid") {
            
            if (row.inn && row.out) {
                let diff_ms = new Date(row.out) - new Date(row.inn);
                if (diff_ms > 0) {
                    total_seconds += (diff_ms / 1000);
                }
            } else {
                missing_punch_days += 1;
            }
        }
    });

    let total_minutes = total_seconds / 60;
    
    let worked_days = working_hours > 0 ? Math.floor(total_minutes / mins_per_day) : 0;
    let remaining_hours = working_hours > 0 ? (total_minutes % mins_per_day) / 60 : total_minutes / 60;

    let final_days = missing_punch_days + worked_days;

    frm.set_value("days_to_be_deducted", final_days);
    frm.set_value("total_days", final_days);
    
    frm.set_value("hours_to_be_deducted", remaining_hours);
    frm.set_value("total_hours", remaining_hours);

    const fields_to_toggle = [
        "total_days", "total_hours", "utilize_it_on", 
        "days_to_be_deducted", "hours_to_be_deducted", 
        "section_break_deductibles"
    ];
    
    fields_to_toggle.forEach(f => frm.set_df_property(f, "hidden", has_selection ? 0 : 1));

    if (typeof handle_dynamic_buttons === "function") {
        handle_dynamic_buttons(frm, selected_row_names);
    }
},
});

function populate_processed_employee_attendance_list(frm) {
    if (frm.is_new()) return;

    frappe.call({
        method: "customized_forcommon.common_customization.doctype.attendance_collection.attendance_collection.get_processed_employee_attendance",
        args: {
            docname: frm.doc.name
        },
        callback: function(r) {
            let html_content = "";

            if (r.message && r.message.length > 0) {
                html_content = `
                    <table class="table table-bordered table-condensed" style="background-color: #fff; font-size: 13px;">
                        <thead>
                            <tr style="background-color: #f8f9fa;">
                                <th>Date</th>
                                <th>In</th>
                                <th>Out</th>
                                <th>Shift</th>
                                <th>Checkin Link</th>
                                <th>Attendance Link</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                r.message.forEach(data => {
                    // Generate internal Desk links
                    let checkin_link = data.employee_checkin 
                        ? `<a href="/app/employee-checkin/${data.employee_checkin}" target="_blank" class="text-info font-weight-bold">${data.employee_checkin}</a>` 
                        : '<span class="text-muted">-</span>';
                    
                    let attendance_link = data.attendance 
                        ? `<a href="/app/attendance/${data.attendance}" target="_blank" class="text-info font-weight-bold">${data.attendance}</a>` 
                        : '<span class="text-muted">-</span>';

                    html_content += `
                        <tr>
                            <td>${frappe.datetime.str_to_user(data.attendance_date)}</td>
                            <td>${data.inn ? frappe.datetime.str_to_user(data.inn) : "-"}</td>
                            <td>${data.out ? frappe.datetime.str_to_user(data.out) : "-"}</td>
                            <td>${data.shift_type || "-"}</td>
                            <td>${checkin_link}</td>
                            <td>${attendance_link}</td>
                        </tr>
                    `;
                });

                html_content += `</tbody></table>`;
            } else {
                html_content = `<div class="text-muted text-center" style="padding: 20px; border: 1px dashed #ccc;">No processed records to display.</div>`;
            }

            // Target the wrapper of your HTML field
            let field_wrapper = frm.get_field("processed_employee_attendance_list").$wrapper;
            field_wrapper.html(html_content);
        }
    });
}


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