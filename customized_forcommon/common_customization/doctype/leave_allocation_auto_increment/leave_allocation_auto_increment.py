# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, date_diff
from datetime import datetime


class LeaveAllocationAutoIncrement(Document):
    def validate(self):
        self.validate_dates()
        self.validate_empty_employees_table()
        self.validate_leave_days_to_be_added()

    def validate_dates(self):
        if self.from_date and self.to_date:
            if getdate(self.to_date) <= getdate(self.from_date):
                frappe.throw("To Date must be greater than From Date")
    def validate_empty_employees_table(self):
        if not self.employees:
            frappe.throw("No Employee is found in the selected filters")

    def validate_leave_days_to_be_added(self):
        if self.filter_by_increment == "Increment This Year":
            if self.leave_days_to_be_added < 1:
                frappe.throw("Leaves to be added cannot be less than 1 day")
    def on_submit(self):
        self.make_allocation()
        if self.status == "Pending":
            frappe.throw("You can't submit with pending status")

    def make_allocation(self):
        from_date = self.from_date
        to_date = self.to_date
        leave_type = self.leave_type
        filter = self.filter_by_increment

        if not self.employees:
            return None
    
        if self.employees:
            for row in self.employees:
                employee = row.employee
                department = row.department
                company = row.company
                total_leaves_allocated = row.leave_allocated

                exists = frappe.db.exists("Leave Allocation", {
                    "employee": employee,
                    "from_date": from_date,
                    "to_date": to_date,
                    "leave_type": leave_type,
                    "docstatus": 1
                })
                if exists:
                    continue  # or skip creating new

                # create a new leave allocation for employees according to the filter
                if filter == "Increment This Year" and self.status == "Allocated":
                    new_leave_allocation = frappe.new_doc("Leave Allocation")
                    new_leave_allocation.employee = employee
                    new_leave_allocation.department = department
                    new_leave_allocation.company = company
                    new_leave_allocation.new_leaves_allocated = total_leaves_allocated + self.leave_days_to_be_added
                    new_leave_allocation.from_date = from_date
                    new_leave_allocation.to_date = to_date
                    new_leave_allocation.leave_type = leave_type
                    new_leave_allocation.save()
                    new_leave_allocation.submit()
                    frappe.db.commit()
                    frappe.msgprint("New Leave Allocated for {}". format(employee))

                elif filter == "Not Increment This Year" and self.status == "Allocated":
                    new_leave_allocation = frappe.new_doc("Leave Allocation")
                    new_leave_allocation.employee = employee
                    new_leave_allocation.department = department
                    new_leave_allocation.company = company
                    new_leave_allocation.new_leaves_allocated = total_leaves_allocated
                    new_leave_allocation.from_date = from_date
                    new_leave_allocation.to_date = to_date
                    new_leave_allocation.leave_type = leave_type
                    new_leave_allocation.save()
                    new_leave_allocation.submit()
                    frappe.db.commit()
                    frappe.msgprint("New Leave Allocated for {}". format(employee))
                elif filter == "Not Allocated Before" and self.status == "Allocated":
                    new_leave_allocation = frappe.new_doc("Leave Allocation")
                    new_leave_allocation.employee = employee
                    new_leave_allocation.department = department
                    new_leave_allocation.company = company
                    new_leave_allocation.new_leaves_allocated = self.leaves_to_be_allocated
                    new_leave_allocation.from_date = from_date
                    new_leave_allocation.to_date = to_date
                    new_leave_allocation.leave_type = leave_type
                    new_leave_allocation.save()
                    new_leave_allocation.submit()
                    frappe.db.commit()
                    frappe.msgprint("Initial New Leave Allocated for {}". format(employee))

@frappe.whitelist(allow_guest=True)
def get_leave_period(leave_period=None, ):
    """
    Returns the leave period for the given leave period name.
    If no leave period is provided, it returns the current leave period.
    """
    if not leave_period:
        return None
    
    lp = frappe.get_doc("Leave Period", leave_period)
    if not lp:
        return None

    return {"to_date": lp.to_date}


@frappe.whitelist(allow_guest=True)
def get_total_leave_days_allocated(leave_type=None):
    
    if not leave_type:
        return None
    total_leaves_allocated = frappe.db.get_value("Leave Type", {"name": leave_type}, "max_leaves_allowed")

    return {"total_leaves_allocated" : total_leaves_allocated}


def get_ethiopian_fiscal_year_range(today=None):
    today = today or datetime.today()
    current_year = today.year
    fy_start = datetime(current_year, 7, 8)
    if today < fy_start:
        fy_start = datetime(current_year - 1, 7, 8)
    fy_end = datetime(fy_start.year + 1, 7, 7)
    return fy_start.date(), fy_end.date()

@frappe.whitelist()
def get_filtered_employees(increment_filter="All", employee_group=None):
    fy_start, fy_end = get_ethiopian_fiscal_year_range()

    filters = {"status": "Active"}
    if employee_group:
        filters["custom_employee_group"] = employee_group

    # Fetch all active employees
    employees = frappe.get_all(
        "Employee",
        filters=filters,
        fields=["name", "employee_name", "company", "department", "custom_next_leave_increment_year"]
    )

    result = []

    for emp in employees:
        emp_name = emp.name
        inc_date = emp.custom_next_leave_increment_year

        # If inc_date is string or datetime, normalize to date for comparison
        if inc_date:
            if isinstance(inc_date, str):
                inc_date = frappe.utils.data.parse_date(inc_date)
            elif hasattr(inc_date, "date"):
                inc_date = inc_date.date()

        # Fetch latest Leave Allocation (docstatus=1 = submitted)
        latest = frappe.db.sql("""
            SELECT name, from_date, to_date, total_leaves_allocated
            FROM `tabLeave Allocation`
            WHERE employee = %s AND docstatus = 1
            ORDER BY to_date DESC LIMIT 1
        """, (emp_name,), as_dict=True)

        latest_allocation = latest[0] if latest else None

        # Filtering logic
        include = False
        if increment_filter == "All Allocated":
            include = latest_allocation is not None

        elif increment_filter == "Increment This Year":
            include = (
                inc_date
                and fy_start <= inc_date <= fy_end
                and latest_allocation
            )

        elif increment_filter == "Not Increment This Year":
            include = (
                latest_allocation is not None and
                (not inc_date or inc_date < fy_start or inc_date > fy_end)
            )

        elif increment_filter == "Not Allocated Before":
            include = latest_allocation is None

        if include:
            result.append({
                "name": emp_name,
                "employee_name": emp.employee_name,
                "department": emp.department,
                "company": emp.company,
                "allocation_id": latest_allocation.name if latest_allocation else None,
                "from_date": latest_allocation.from_date if latest_allocation else None,
                "to_date": latest_allocation.to_date if latest_allocation else None,
                "leave_allocated": latest_allocation.total_leaves_allocated if latest_allocation else None
            })

    return result