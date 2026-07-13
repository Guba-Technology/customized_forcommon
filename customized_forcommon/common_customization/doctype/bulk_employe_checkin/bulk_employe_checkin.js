// Copyright (c) 2026, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Employe Checkin', {
    refresh: function(frm) {
        // Clear any duplicate buttons to prevent rendering stacking
        frm.remove_custom_button(__('Process Bulk Check-in'), __("Actions"));
        
        // Add the action button inside the Actions dropdown menu
        frm.add_custom_button(__('Process Bulk Check-in'), function() {
            frm.trigger('process_bulk_checkin');
        }, __("Actions"));
    },

    from_date: function(frm) { frm.trigger('fetch_employees'); },
    to_date: function(frm) { frm.trigger('fetch_employees'); },
    shift: function(frm) { frm.trigger('fetch_employees'); },
    checkin_type: function(frm) { frm.trigger('fetch_employees'); },

    fetch_employees: function(frm) {
        if (!frm.doc.from_date || !frm.doc.to_date) return;

        frappe.call({
            method: "customized_forcommon.common_customization.doctype.bulk_employe_checkin.bulk_employe_checkin.get_eligible_employees",
            args: {
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
                checkin_type: frm.doc.checkin_type,
                shift: frm.doc.shift
            },
            callback: function(r) {
                if (r.message) {
                    frm.clear_table('employee_list');
                    r.message.forEach(emp => {
                        let row = frm.add_child('employee_list');
                        row.employee = emp.name;
                        row.shift = emp.default_shift;
                    });
                    frm.refresh_field('employee_list');
                }
            }
        });
    },

    process_bulk_checkin: function(frm) {
        if (!frm.doc.checkin_type || !frm.doc.time) {
            frappe.msgprint(__('Please fill Checkin Type and Time before processing.'));
            return;
        }
        if (!frm.doc.employee_list || frm.doc.employee_list.length === 0) {
            frappe.msgprint(__('Employee List is empty.'));
            return;
        }

        frappe.confirm(__('Are you sure you want to create checkin records for {0} employees?', [frm.doc.employee_list.length]), () => {
            frappe.call({
                method: "customized_forcommon.common_customization.doctype.bulk_employe_checkin.bulk_employe_checkin.create_bulk_checkins",
                args: {
                    employees: frm.doc.employee_list,
                    log_type: frm.doc.checkin_type,
                    time: frm.doc.time
                },
                freeze: true,
                freeze_message: __("Processing Bulk Checkins..."),
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.msgprint({
                            title: __('Success'),
                            indicator: 'green',
                            message: __('Successfully created {0} Employee Checkin records.', [r.message.count])
                        });
                        frm.clear_table('employee_list');
                        frm.set_value('checkin_type', '');
                        frm.set_value('time', '');
                        frm.refresh_field('employee_list');
                    }
                }
            });
        });
    }
});