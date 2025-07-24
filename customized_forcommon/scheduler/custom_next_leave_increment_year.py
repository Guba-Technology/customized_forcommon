import frappe
from datetime import datetime, date

def get_ethiopian_fiscal_year_start():
    today = datetime.today().date()
    year = today.year

    fy_start = date(year, 7, 8)  # Fiscal year starts July 8

    if today < fy_start:
        year -= 1
        fy_start = date(year, 7, 8)

    return year, fy_start

def execute():
    today = datetime.today().date()
    fiscal_year_start_year, fy_start = get_ethiopian_fiscal_year_start()

    employees = frappe.get_all("Employee", filters={"status": "Active"}, fields=[
        "name",
        "custom_leave_increment_period",
        "date_of_joining",
        "custom_next_leave_increment_year"
    ])

    for emp in employees:
        period = emp.custom_leave_increment_period
        doj = emp.date_of_joining
        next_increment_date = emp.custom_next_leave_increment_year

        if not (period and doj):
            continue

        if isinstance(doj, str):
            doj = datetime.strptime(doj, "%Y-%m-%d").date()

        fiscal_year_start = date(fiscal_year_start_year, 7, 8)

        years_passed = fiscal_year_start.year - doj.year
        increments_completed = years_passed // period
        next_increment_year = doj.year + (increments_completed * period)

        if date(next_increment_year, 7, 8) <= fiscal_year_start:
            next_increment_year += period

        new_date = date(next_increment_year, 7, 8)

        if next_increment_date and isinstance(next_increment_date, str):
            next_increment_date = datetime.strptime(next_increment_date, "%Y-%m-%d").date()

        if not next_increment_date or next_increment_date != new_date:
            frappe.db.set_value("Employee", emp.name, "custom_next_leave_increment_year", new_date)
            frappe.db.commit()
