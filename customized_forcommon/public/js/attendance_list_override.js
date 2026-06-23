// Overwrite the indicator as usual
const original_get_indicator = frappe.listview_settings["Attendance"].get_indicator;
frappe.listview_settings["Attendance"].get_indicator = function (doc) {
    if (doc.status === "On Education") {
        return [__("On Education"), "blue", "status,=,On Education"];
    }
    return original_get_indicator(doc);
};

// Clean Rewrite: Completely overwrite the original onload function
frappe.listview_settings["Attendance"].onload = function (list_view) {
    let me = this;

    list_view.page.add_inner_button(__("Mark Attendance"), function () {
        let first_day_of_month = moment().startOf("month");

        if (moment().toDate().getDate() === 1) {
            first_day_of_month = first_day_of_month.subtract(1, "month");
        }

        let dialog = new frappe.ui.Dialog({
            title: __("Mark Attendance"),
            fields: [
                {
                    fieldname: "employee",
                    label: __("For Employee"),
                    fieldtype: "Link",
                    options: "Employee",
                    get_query: () => {
                        return {
                            query: "erpnext.controllers.queries.employee_query",
                        };
                    },
                    reqd: 1,
                    onchange: () => me.reset_dialog(dialog),
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
                    default: first_day_of_month.toDate(),
                    onchange: () => me.get_unmarked_days(dialog),
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
                    default: moment().toDate(),
                    onchange: () => me.get_unmarked_days(dialog),
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
                    // Added "On Education" directly into the configuration array here
                    options: ["Present", "Absent", "Half Day", "Work From Home", "On Education"],
                    reqd: 1,
                },
                {
                    label: __("Exclude Holidays"),
                    fieldtype: "Check",
                    fieldname: "exclude_holidays",
                    onchange: () => me.get_unmarked_days(dialog),
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
            primary_action(data) {
                if (cur_dialog.no_unmarked_days_left) {
                    frappe.msgprint(
                        __(
                            "Attendance from {0} to {1} has already been marked for the Employee {2}",
                            [data.from_date, data.to_date, data.employee],
                        ),
                    );
                } else {
                    frappe.confirm(
                        __("Mark attendance as {0} for {1} on selected dates?", [
                            data.status,
                            data.employee,
                        ]),
                        () => {
                            frappe.call({
                                method: "hrms.hr.doctype.attendance.attendance.mark_bulk_attendance",
                                args: {
                                    data: data,
                                },
                                callback: function (r) {
                                    if (r.message === 1) {
                                        frappe.show_alert({
                                            message: __("Attendance Marked"),
                                            indicator: "blue",
                                        });
                                        cur_dialog.hide();
                                    }
                                },
                            });
                        },
                    );
                }
                dialog.hide();
                list_view.refresh();
            },
            primary_action_label: __("Mark Attendance"),
        });
        dialog.show();
    });
};