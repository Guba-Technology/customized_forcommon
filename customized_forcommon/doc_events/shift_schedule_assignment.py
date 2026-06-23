import frappe
from frappe import _
from frappe.utils import add_days, format_date, get_link_to_form, get_weekday, getdate, nowdate
from hrms.hr.doctype.shift_assignment_tool.shift_assignment_tool import create_shift_assignment



def custom_on_update(doc, method=None):
    start_date = getattr(doc, "start_date", None)
    create_shifts_after = getattr(doc, "create_shifts_after", None)
    target_start = create_shifts_after or start_date
    if target_start:
        create_shifts_for_doc(doc, target_start)


def create_shifts_for_doc(doc, start_date: str, end_date: str | None = None) -> None:
    shift_schedule = frappe.get_doc("Shift Schedule", doc.shift_schedule)
    gap = {
        "Every Week": 0,
        "Every 2 Weeks": 1,
        "Every 3 Weeks": 2,
        "Every 4 Weeks": 3,
    }[shift_schedule.frequency]
    date = start_date
    individual_assignment_start = None
    week_end_day = get_weekday(getdate(add_days(start_date, -1)))
    repeat_on_days = [day.day for day in shift_schedule.repeat_on_days]
    if not end_date:
        end_date = doc.custom_shift_end_date or add_days(start_date, 90)
    while date <= end_date:
        weekday = get_weekday(getdate(date))
        if weekday in repeat_on_days:
            if not individual_assignment_start:
                individual_assignment_start = date
            if date == end_date:
                create_individual_assignment(
                    doc, shift_schedule.shift_type, individual_assignment_start, date
                )
        elif individual_assignment_start:
            create_individual_assignment(
                doc, shift_schedule.shift_type, individual_assignment_start, add_days(date, -1)
            )
            individual_assignment_start = None
        if weekday == week_end_day and gap:
            if individual_assignment_start:
                create_individual_assignment(
                    doc, shift_schedule.shift_type, individual_assignment_start, date
                )
                individual_assignment_start = None
            date = add_days(date, 7 * gap)
        date = add_days(date, 1)


def create_individual_assignment(doc, shift_type, start_date, end_date):
    create_shift_assignment(
        doc.employee,
        doc.company,
        shift_type,
        start_date,
        end_date,
        doc.shift_status,
        doc.shift_location,
        shift_schedule_assignment=doc.name,
    )
    doc.db_set("create_shifts_after", end_date, update_modified=False)


def process_auto_shift_creation():
    shift_schedule_assignments = frappe.get_all(
        "Shift Schedule Assignment",
        filters={"enabled": 1, "create_shifts_after": ["<=", nowdate()]},
        pluck="name",
    )
    for d in shift_schedule_assignments:
        try:
            doc = frappe.get_doc("Shift Schedule Assignment", d)
            start_date = doc.create_shifts_after
            create_shifts_for_doc(doc, add_days(doc.create_shifts_after, 1))
            text = _(
                "Shift Assignments created for the schedule between {0} and {1} via background job"
            ).format(frappe.bold(format_date(start_date)), frappe.bold(format_date(doc.create_shifts_after)))
            doc.add_comment(comment_type="Info", text=text)
        except Exception as e:
            frappe.log_error(e)
            continue