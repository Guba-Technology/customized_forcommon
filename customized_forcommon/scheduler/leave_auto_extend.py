import frappe
from frappe.utils import getdate, add_years, add_days, nowdate

def auto_extend_leave_allocations():
    today = getdate(nowdate())

    # Get all finalized Annual Leave Allocations with auto increment
    allocations = frappe.get_all("Leave Allocation", 
        filters={
            "leave_type": "Annual",
            "docstatus": 1
        },
        fields=["name", "employee", "from_date", "to_date", "new_leaves_allocated", "auto_increment_period"]
    )

    for alloc in allocations:
        if not alloc.custom_auto_increment_period:
            continue

        original_from = getdate(alloc.from_date)
        original_to = getdate(alloc.to_date)

        next_from = add_years(original_from, 1)
        next_to = add_years(original_to, 1)

        # Check if the next year already exists
        exists = frappe.db.exists("Leave Allocation", {
            "employee": alloc.employee,
            "leave_type": "Annual Leave",
            "from_date": next_from
        })
        if exists:
            continue

        # Determine how many years have passed from the original allocation
        years_since_original = next_from.year - original_from.year

        # Add 1 day to to_date only if years_since_original is divisible by auto_increment_period
        if years_since_original % int(alloc.custom_auto_increment_period) == 0:
            next_to = add_days(next_to, 1)

        doc = frappe.new_doc("Leave Allocation")
        doc.update({
            "employee": alloc.employee,
            "leave_type": alloc.leave_type,
            "from_date": next_from,
            "to_date": next_to,
            "new_leaves_allocated": alloc.new_leaves_allocated,
            "auto_increment_period": alloc.custom_auto_increment_period,
            "description": f"Auto-generated from {alloc.name}"
        })
        doc.save()

    frappe.db.commit()
