# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate
from erpnext.stock.report.stock_analytics.stock_analytics import get_period, get_period_date_ranges


def execute(filters=None):
    columns, data = [], []
    data = get_data(filters)
    columns = get_columns(filters)
    chart_data = get_chart_data(data, filters)  # Updated to filter status
    return columns, data, None, chart_data


def get_data(filters):
    query_filters = {
        "docstatus": ("<", 2),
        "posting_date": ("between", [filters.from_date, filters.to_date]),
    }

    fields = [
        "name",
        "status",
        "work_order",
        "production_item",
        "item_name",
        "posting_date",
        "total_completed_qty",
        "workstation",
        "operation",
        "total_time_in_mins",
    ]

    for field in ["work_order", "production_item"]:
        if filters.get(field):
            query_filters[field] = ("in", filters.get(field))

    for field in ["workstation", "operation", "status", "company"]:
        if filters.get(field):
            query_filters[field] = filters.get(field)

    data = frappe.get_all("Job Card", fields=fields, filters=query_filters)

    if not data:
        return []

    job_cards = [d.name for d in data]

    job_card_time_filter = {
        "docstatus": ("<", 2),
        "parent": ("in", job_cards),
    }

    job_card_time_details = {}
    for job_card_data in frappe.get_all(
        "Job Card Time Log",
        fields=["min(from_time) as from_time", "max(to_time) as to_time", "parent"],
        filters=job_card_time_filter,
        group_by="parent",
    ):
        job_card_time_details[job_card_data.parent] = job_card_data

    res = []
    for d in data:
        # Default to "Open" if status is not set
        if d.status not in ["Open", "Completed", "Work In Progress"]:
            d.status = "Open"

        # Handle job card time details
        if job_card_time_details.get(d.name):
            d.from_time = job_card_time_details.get(d.name).from_time
            d.to_time = job_card_time_details.get(d.name).to_time

        res.append(d)

    return res


def get_chart_data(job_card_details, filters):
    """
    Generates the chart data based on the selected status filter
    - If no status filter is applied, it includes all statuses
    - If a specific status is selected, it shows only that status in the chart
    """
    labels, periodic_data = prepare_chart_data(job_card_details, filters)

    datasets = []
    selected_statuses = []

    # Check if a specific status filter is applied
    if filters.get("status"):
        # Only one status is selected via filter (e.g., "Open" or "Work In Progress")
        selected_statuses = [filters.status]
    else:
        # No status filter: include both Open and Completed
        selected_statuses = ["Open", "Completed", "Work In Progress"]

    # Add dataset for each selected status
    for status in selected_statuses:
        values = []
        for period in labels:
            values.append(periodic_data.get(status, {}).get(period, 0))
        datasets.append({"name": _(status), "values": values})

    # Prepare chart
    chart = {"data": {"labels": labels, "datasets": datasets}, "type": "bar"}
    return chart


def prepare_chart_data(job_card_details, filters):
    """
    Prepares the chart data for job cards by grouping them based on their status (Open/Completed/Work In Progress)
    and period (monthly range).
    """
    labels = []

    # Initialize a dictionary to hold data for each status
    periodic_data = {
        "Open": {},
        "Completed": {},
        "Work In Progress": {},
        "On Hold": {},
    }

    # Ensure filtering by monthly range
    filters.range = "Monthly"
    ranges = get_period_date_ranges(filters)

    for from_date, end_date in ranges:
        period = get_period(end_date, filters)
        if period not in labels:
            labels.append(period)

        # For each job card, check the status and count the occurrences in the relevant period
        for d in job_card_details:
            if getdate(d.posting_date) > from_date and getdate(d.posting_date) <= end_date:
                status = d.status if d.status else "Open"  # Default to Open if no status

                # Ensure we are counting only the statuses we're interested in
                if status in periodic_data:
                    if periodic_data[status].get(period):
                        periodic_data[status][period] += 1
                    else:
                        periodic_data[status][period] = 1

    return labels, periodic_data


def get_columns(filters):
    columns = [
        {
            "label": _("Id"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Job Card",
            "width": 100,
        },
        {"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Status"), "fieldname": "status", "width": 100},
        {
            "label": _("Work Order"),
            "fieldname": "work_order",
            "fieldtype": "Link",
            "options": "Work Order",
            "width": 100,
        },
        {
            "label": _("Production Item"),
            "fieldname": "production_item",
            "fieldtype": "Link",
            "options": "Item",
            "width": 110,
        },
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 100},
        {
            "label": _("Workstation"),
            "fieldname": "workstation",
            "fieldtype": "Link",
            "options": "Workstation",
            "width": 110,
        },
        {
            "label": _("Operation"),
            "fieldname": "operation",
            "fieldtype": "Link",
            "options": "Operation",
            "width": 110,
        },
        {
            "label": _("Total Completed Qty"),
            "fieldname": "total_completed_qty",
            "fieldtype": "Float",
            "width": 120,
        },
        {"label": _("From Time"), "fieldname": "from_time", "fieldtype": "Datetime", "width": 120},
        {"label": _("To Time"), "fieldname": "to_time", "fieldtype": "Datetime", "width": 120},
        {
            "label": _("Time Required (In Mins)"),
            "fieldname": "total_time_in_mins",
            "fieldtype": "Float",
            "width": 100,
        },
     
    ]

    return columns
