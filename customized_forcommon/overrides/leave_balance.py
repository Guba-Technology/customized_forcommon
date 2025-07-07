import frappe
from frappe.utils import getdate
from hrms.hr.doctype.leave_application.leave_application import get_leave_entries
import datetime


def get_leaves_for_period(
    employee: str,
    leave_type: str,
    from_date: datetime.date,
    to_date: datetime.date,
    skip_expired_leaves: bool = True,
) -> float:
    leave_entries = get_leave_entries(employee, leave_type, from_date, to_date)
    leave_days = 0

    for leave_entry in leave_entries:
        inclusive_period = leave_entry.from_date >= getdate(from_date) and leave_entry.to_date <= getdate(to_date)

        # Leave Encashment
        if inclusive_period and leave_entry.transaction_type == "Leave Encashment":
            leave_days += leave_entry.leaves

        # Expired Allocations (if not skipped)
        elif (
            inclusive_period
            and leave_entry.transaction_type == "Leave Allocation"
            and leave_entry.is_expired
            and not skip_expired_leaves
        ):
            leave_days += leave_entry.leaves

        # Leave Application → use total_leave_days always
        elif leave_entry.transaction_type == "Leave Application":
            total_days = frappe.db.get_value("Leave Application", leave_entry.transaction_name, "total_leave_days")
            if total_days is not None:
                leave_days += -1 * float(total_days)  # Negative since it's consumption
            else:
                # Fallback: Assume full-day leave (default behavior)
                diff_days = (getdate(leave_entry.to_date) - getdate(leave_entry.from_date)).days + 1
                leave_days += -1 * diff_days

    return leave_days
