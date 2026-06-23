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

    fy = frappe.get_doc("Fiscal Year", filters["fiscal_year"])

    start_date = getdate(fy.year_start_date)
    end_date = getdate(fy.year_end_date)

    months = build_months(start_date, end_date)

    columns = get_columns()
    data, totals = get_data(months)

    # ---------------- ANNUAL ROW ----------------
    # data.append({})  # blank separator row

    data.append({
        "month": "",
        "beginning": "Annual",
        "hires": totals["hires"],
        "separation": totals["separation"],
        "end": round(totals["avg_end"], 2),
        "turnover": (
            totals["separation"] / totals["avg_end"]
            if totals["avg_end"] else 0
        )
    })

    return columns, data


# ---------------- COLUMNS ----------------
def get_columns():
    return [
        {"label": _("No"), "fieldname": "idx", "fieldtype": "Data", "width": 80},
        {"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 140},
        {"label": _("Beginning Employees"), "fieldname": "beginning", "fieldtype": "Data", "width": 260},
        {"label": _("New Hires"), "fieldname": "hires", "fieldtype": "Int", "width": 120},
        {"label": _("Separation"), "fieldname": "separation", "fieldtype": "Int", "width": 120},
        {"label": _("Average or End Employees"), "fieldname": "end", "fieldtype": "Int", "width": 340},
        {"label": _("Turnover"), "fieldname": "turnover", "fieldtype": "Percent", "width": 130},
    ]


# ---------------- DATA ----------------
def get_data(months):
    data = []

    totals = {
        "hires": 0,
        "separation": 0,
        "end_list": []
    }
    idx = 1

    for i, m in enumerate(months):

        start = m["start"]
        end = m["end"]

        beginning = get_active(start - relativedelta(days=1))
        end_emp = get_active(end)

        hires = frappe.db.count("Employee", {
            "date_of_joining": ["between", [start, end]]
        })

        separation = frappe.db.count("Employee", {
            "relieving_date": ["between", [start, end]]
        })

        turnover = (separation / end_emp) if end_emp else 0

        data.append({
            "idx": idx,
            "month": m["name"],
            "beginning": beginning,
            "hires": hires,
            "separation": separation,
            "end": end_emp,
            "turnover": turnover
        })

        totals["hires"] += hires
        totals["separation"] += separation
        totals["end_list"].append(end_emp)
        idx += 1

    totals["avg_end"] = sum(totals["end_list"]) / len(totals["end_list"])

    return data, totals


# ---------------- SNAPSHOT ----------------
def get_active(date_value):
    joined = frappe.db.count("Employee", {
        "date_of_joining": ["<=", date_value]
    })

    left = frappe.db.count("Employee", {
        "relieving_date": ["<=", date_value]
    })

    return joined - left


# ---------------- MONTHS ----------------
def build_months(start_date, end_date):
    months = []

    current = start_date.replace(day=1)

    seen = set() 

    while current <= end_date:
        key = current.strftime("%Y-%m")

        if key in seen:
            break
        seen.add(key)

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