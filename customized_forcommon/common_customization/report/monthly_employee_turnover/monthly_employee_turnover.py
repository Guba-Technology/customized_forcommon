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

    # IMPORTANT: normalize start month only (ignore FY end to avoid July duplication)
    start_date = fy.year_start_date.replace(day=1)

    months = build_months(start_date)

    columns = get_columns()
    data, totals = get_data(months)

    # ---------------- ANNUAL ROW ----------------
    data.append({
        "idx": "",
        "month": "Annual",
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
        {"label": _("No"), "fieldname": "idx", "fieldtype": "Int", "width": 60},
        {"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 140},
        {"label": _("Beginning Employees"), "fieldname": "beginning", "fieldtype": "Data", "width": 200},
        {"label": _("New Hires"), "fieldname": "hires", "fieldtype": "Int", "width": 120},
        {"label": _("Separation"), "fieldname": "separation", "fieldtype": "Int", "width": 120},
        {
            "label": _("Average Employees"),
            "fieldname": "end",
            "fieldtype": "Float",
            "precision": 2,
            "width": 200
        },
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

    for idx, m in enumerate(months, start=1):

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

    totals["avg_end"] = sum(totals["end_list"]) / len(totals["end_list"])

    return data, totals


# ---------------- SNAPSHOT EMPLOYEE COUNT ----------------
def get_active(date_value):
    joined = frappe.db.count("Employee", {
        "date_of_joining": ["<=", date_value]
    })

    left = frappe.db.count("Employee", {
        "relieving_date": ["<=", date_value]
    })

    return joined - left


# ---------------- FIXED MONTH GENERATOR (NO DUPLICATES) ----------------
def build_months(start_date):
    months = []

    current = start_date.replace(day=1)

    # ALWAYS exactly 12 months → prevents July duplication forever
    for _ in range(12):
        month_start = current

        month_end = (
            month_start
            + relativedelta(months=1)
            - relativedelta(days=1)
        )

        months.append({
            "name": month_start.strftime("%B"),
            "start": month_start,
            "end": month_end,
        })

        current += relativedelta(months=1)

    return months