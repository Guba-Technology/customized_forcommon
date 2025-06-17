// Copyright (c) 2025, Guba Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Clearance', {
    onload: function(frm) {
        // Hide "Add Row" button
        frm.get_field('clearance_table').grid.cannot_add_rows = true;

        // Hide "Delete" option for rows (the trash icon that appears on hover/selection)
        frm.get_field('clearance_table').grid.cannot_delete_rows = true;

        // Hide the entire toolbar of the table, which includes "Select All" checkbox and bulk actions
        frm.get_field('clearance_table').grid.hide_toolbar = true;

        // Additionally, for good measure, and to explicitly hide the checkboxes if they still appear:
        // This targets the specific CSS class for the checkboxes in each row.
        // It's often necessary if hide_toolbar doesn't fully remove the column itself.
        setTimeout(() => {
            frm.fields_dict['clearance_table'].grid.wrapper.find('.grid-row-check').hide();
            // Also hide the delete button that appears on individual rows
            frm.fields_dict['clearance_table'].grid.wrapper.find('.grid-delete-row').hide();
        }, 100); // A small delay to ensure the grid elements are rendered

        frm.refresh_field('clearance_table');
    },

    refresh: function(frm) {
        // Re-apply hiding on refresh, as the grid might re-render
        frm.get_field('clearance_table').grid.cannot_add_rows = true;
        frm.get_field('clearance_table').grid.cannot_delete_rows = true;
        frm.get_field('clearance_table').grid.hide_toolbar = true;

        setTimeout(() => {
            frm.fields_dict['clearance_table'].grid.wrapper.find('.grid-row-check').hide();
            frm.fields_dict['clearance_table'].grid.wrapper.find('.grid-delete-row').hide();
        }, 100);

        frm.refresh_field('clearance_table');
    },

    add_template: function (frm) {
        frappe.prompt([
            {
                label: 'Clearance Template',
                fieldname: 'template',
                fieldtype: 'Link',
                options: 'Clearance Template',
                reqd: 1
            }
        ],
        function (values) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Clearance Template',
                    name: values.template
                },
                callback: function (response) {
                    let template_doc = response.message;

                    if (template_doc && template_doc.clearance_template_table?.length > 0) {
                        frm.clear_table('clearance_table');

                        template_doc.clearance_template_table.forEach(row => {
                            let new_row = frm.add_child('clearance_table');
                            new_row.department = row.department;
                            new_row.status = 'Pending';
                        });

                        frm.refresh_field('clearance_table');

                        // Re-apply the hiding logic after rows are added
                        frm.get_field('clearance_table').grid.cannot_add_rows = true;
                        frm.get_field('clearance_table').grid.cannot_delete_rows = true;
                        frm.get_field('clearance_table').grid.hide_toolbar = true;

                        setTimeout(() => {
                            frm.fields_dict['clearance_table'].grid.wrapper.find('.grid-row-check').hide();
                            frm.fields_dict['clearance_table'].grid.wrapper.find('.grid-delete-row').hide();
                        }, 100);

                        frm.refresh_field('clearance_table');

                        frappe.msgprint(__('Template applied successfully.'));
                    } else {
                        frappe.msgprint(__('Selected template has no departments.'));
                    }
                }
            });
        },
        __('Select Template'),
        __('Apply'));
    }
});