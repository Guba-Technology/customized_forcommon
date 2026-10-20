// Overwrite the indicator as usual
const original_get_indicator = frappe.listview_settings["Attendance"].get_indicator;
frappe.listview_settings["Attendance"].get_indicator = function (doc) {
    if (doc.status === "On Education") {
        return [__("On Education"), "blue", "status,=,On Education"];
    }
    return original_get_indicator(doc);
};

// Clean rewrite: completely overwrite the original onload function
frappe.listview_settings["Attendance"].onload = function (list_view) {
    list_view.page.add_inner_button(__("Mark Attendance"), function () {
        let first_day_of_month = moment().startOf("month");

        if (moment().date() === 1) {
            first_day_of_month = first_day_of_month.subtract(1, "month");
        }

        // Declared first so the guard in load_days is safe while the dialog
        // (and the Ethiopian date control) fires onchange during construction.
        let dialog;

        // Self-contained replacement for me.get_unmarked_days / me.reset_dialog
        const load_days = () => {
            if (!dialog) return;

            const employee = dialog.get_value("employee");
            const from_date = dialog.get_value("from_date");
            const to_date = dialog.get_value("to_date");
            if (!employee || !from_date || !to_date) return;

            frappe.call({
                method: "hrms.hr.doctype.attendance.attendance.get_unmarked_days",
                args: {
                    employee,
                    from_date,
                    to_date,
                    exclude_holidays: dialog.get_value("exclude_holidays") ? 1 : 0,
                },
                callback(r) {
                    const days = r.message || [];
                    dialog.no_unmarked_days_left = !days.length;

                    const field = dialog.fields_dict.unmarked_days;
                    field.df.options = days.map((d) => ({ label: d, value: d, checked: 1 }));
                    field.refresh();

                    dialog.set_df_property("time_period_section", "hidden", 0);
                    dialog.set_df_property("days_section", "hidden", 0);
                },
            });
        };

        dialog = new frappe.ui.Dialog({
            title: __("Mark Attendance"),
            fields: [
                {
                    fieldname: "employee",
                    label: __("For Employee"),
                    fieldtype: "Link",
                    options: "Employee",
                    get_query: () => ({
                        query: "erpnext.controllers.queries.employee_query",
                    }),
                    reqd: 1,
                    onchange: () => load_days(),
                },
                {
                    fieldtype: "Section Break",
                    fieldname: "time_period_section",
                    hidden: 1,
                },
                {
                    label: __("Start"),
                    fieldtype: "Date",
                    fieldname: "from_date",
                    reqd: 1,
                    // String, not Date object: the Ethiopian control calls value.split()
                    default: first_day_of_month.format("YYYY-MM-DD"),
                    onchange: () => load_days(),
                },
                {
                    fieldtype: "Column Break",
                    fieldname: "time_period_column",
                },
                {
                    label: __("End"),
                    fieldtype: "Date",
                    fieldname: "to_date",
                    reqd: 1,
                    default: moment().format("YYYY-MM-DD"),
                    onchange: () => load_days(),
                },
                {
                    fieldtype: "Section Break",
                    fieldname: "days_section",
                    hidden: 1,
                },
                {
                    label: __("Status"),
                    fieldtype: "Select",
                    fieldname: "status",
                    options: ["Present", "Absent", "Half Day", "Work From Home", "On Education"],
                    reqd: 1,
                },
                {
                    label: __("Exclude Holidays"),
                    fieldtype: "Check",
                    fieldname: "exclude_holidays",
                    onchange: () => load_days(),
                },
                {
                    label: __("Unmarked Attendance for days"),
                    fieldname: "unmarked_days",
                    fieldtype: "MultiCheck",
                    options: [],
                    columns: 2,
                    select_all: true,
                },
            ],
            primary_action_label: __("Mark Attendance"),
            primary_action(data) {
                if (dialog.no_unmarked_days_left) {
                    frappe.msgprint(
                        __(
                            "Attendance from {0} to {1} has already been marked for the Employee {2}",
                            [data.from_date, data.to_date, data.employee],
                        ),
                    );
                    return;
                }

                frappe.confirm(
                    __("Mark attendance as {0} for {1} on selected dates?", [
                        data.status,
                        data.employee,
                    ]),
                    () => {
                        frappe.call({
                            method: "hrms.hr.doctype.attendance.attendance.mark_bulk_attendance",
                            args: { data },
                            callback(r) {
                                if (r.message === 1) {
                                    frappe.show_alert({
                                        message: __("Attendance Marked"),
                                        indicator: "blue",
                                    });
                                    dialog.hide();
                                    list_view.refresh();
                                }
                            },
                        });
                    },
                );
            },
        });

        dialog.show();
    });
};