# Copyright (c) 2026, Guba Technology and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate
from dateutil.relativedelta import relativedelta


def execute(filters=None):
    filters = filters or {}

    if not filters.get("fiscal_year"):
        frappe.throw(_("Fiscal Year is required"))

    fiscal_year = frappe.get_doc("Fiscal Year", filters["fiscal_year"])

    start_date = getdate(fiscal_year.year_start_date)
    end_date = getdate(fiscal_year.year_end_date)

    months = build_months(start_date, end_date)

    columns = get_columns()
    data = get_data(months)

    return columns, data


# ---------------- COLUMNS ----------------
def get_columns():
    return [
        {"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 140},
        {"label": _("Beginning Employees"), "fieldname": "beginning", "fieldtype": "Int", "width": 160},
        {"label": _("New Hires"), "fieldname": "hires", "fieldtype": "Int", "width": 120},
        {"label": _("Separation"), "fieldname": "separation", "fieldtype": "Int", "width": 120},
        {"label": _("End Employees"), "fieldname": "end", "fieldtype": "Int", "width": 140},
        {"label": _("Turnover"), "fieldname": "turnover", "fieldtype": "Percent", "width": 130},
    ]


# ---------------- DATA ----------------
def get_data(months):
    data = []

    for m in months:
        start = m["start"]
        end = m["end"]

        # ACTIVE employees at START (snapshot)
        beginning = get_active_employees(start - relativedelta(days=1))

        # ACTIVE employees at END
        end_employees = get_active_employees(end)

        # HIRES within month
        hires = frappe.db.count(
            "Employee",
            {
                "date_of_joining": ["between", [start, end]]
            }
        )

        # SEPARATIONS within month
        separation = frappe.db.count(
            "Employee",
            {
                "relieving_date": ["between", [start, end]]
            }
        )

        turnover = (separation / end_employees) if end_employees else 0

        data.append({
            "month": m["name"],
            "beginning": beginning,
            "hires": hires,
            "separation": separation,
            "end": end_employees,
            "turnover": turnover
        })

    return data


# ---------------- SNAPSHOT EMPLOYEE COUNT ----------------
def get_active_employees(date_value):
    joined = frappe.db.count("Employee", {
        "date_of_joining": ["<=", date_value]
    })

    left = frappe.db.count("Employee", {
        "relieving_date": ["<=", date_value]
    })

    return joined - left

# ---------------- MONTH GENERATOR ----------------
def build_months(start_date, end_date):
    months = []
    current = start_date.replace(day=1)

    while current <= end_date:
        next_month = current + relativedelta(months=1)
        month_end = next_month - relativedelta(days=1)

        if month_end > end_date:
            month_end = end_date

        months.append({
            "name": current.strftime("%B"),
            "start": current,
            "end": month_end
        })

        current = next_month

    return months