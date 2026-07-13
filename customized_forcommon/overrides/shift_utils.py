import frappe
from frappe.utils import add_days, getdate, date_diff
def generate_three_shift_rotation_for_all_assignments():
    ssa_docs = frappe.get_all("Shift Schedule Assignment", fields=["name"])
    for doc in ssa_docs:
        assignment_doc = frappe.get_doc("Shift Schedule Assignment", doc.name)
        if assignment_doc:
            generate_three_shift_rotation(assignment_doc)

def generate_three_shift_rotation(assignment_doc):
    """
    Generates Shift Assignments from (create_shifts_after + 1) up to custom_shift_end_date.
    Rotates between shift_type, shift_2, and shift_3 based on a weekly cadence 
    matching the repeat_on_days child table configuration.
    """
    
    if not (assignment_doc.create_shifts_after and assignment_doc.custom_shift_end_date):
        return

    # Fetch the template settings
    schedule = frappe.get_doc("Shift Schedule", assignment_doc.shift_schedule)
    
    # Store our 3 core shifts into an indexable list
    shifts_pool = [schedule.shift_type, schedule.shift_2, schedule.shift_3]
    # Filter out empty fields to establish rotation loop count (1, 2, or 3 shifts)
    active_shifts = [s for s in shifts_pool if s]
    
    if not active_shifts:
        return

    # Build a quick lookup dictionary for days configured to repeat (e.g., {"Monday": 1, "Tuesday": 1})
    allowed_days = {row.day: True for row in schedule.repeat_on_days}

    # Start generating the day after the current threshold
    current_date = add_days(getdate(assignment_doc.create_shifts_after), 1)
    end_date = getdate(assignment_doc.custom_shift_end_date)

    while current_date <= end_date:
        day_of_week = current_date.strftime("%A")

        # Only proceed if this specific day of the week is active in repeat_on_days
        if allowed_days.get(day_of_week):
            # Calculate how many weeks have passed since the original base start date 
            # to determine the current active shift rotation index
            weeks_elapsed = date_diff(current_date, assignment_doc.start_date) // 7
            shift_index = weeks_elapsed % len(active_shifts)
            assigned_shift = active_shifts[shift_index]

            # Enforce duplicate checking parameters
            exists = frappe.db.exists("Shift Assignment", {
                "employee": assignment_doc.employee,
                "start_date": current_date,
                "docstatus": ["<", 2]
            })

            if not exists:
                doc = frappe.new_doc("Shift Assignment")
                doc.employee = assignment_doc.employee
                doc.shift_type = assigned_shift
                doc.start_date = current_date
                doc.end_date = current_date
                doc.company = assignment_doc.company
                doc.shift_location = assignment_doc.shift_location
                doc.status = "Approved"
                doc.insert(ignore_permissions=True)
                doc.submit()

        current_date = add_days(current_date, 1)