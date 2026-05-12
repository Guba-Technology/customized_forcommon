import frappe
from frappe import _
from frappe.query_builder.functions import Count

def custom_employee_analytics_execute(filters=None):
    filters = frappe._dict(filters or {})

    if not filters.company:
        frappe.throw(_("Please select a Company first."))

    # 1. Define Base Columns (Always Shown)
    columns = [
        {"label": _("ID"), "fieldname": "name", "fieldtype": "Link", "options": "Employee", "width": 120},
        {"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 160},
        {"label": _("Date of Birth"), "fieldname": "date_of_birth", "fieldtype": "Date", "width": 110},
        {"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 120},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 120},
        {"label": _("Designation"), "fieldname": "designation", "fieldtype": "Link", "options": "Designation", "width": 120},
        {"label": _("Gender"), "fieldname": "gender", "fieldtype": "Data", "width": 100},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100}
    ]

    # 2. Define standard fields to fetch for all queries
    standard_fields = [
        "name", "employee_name", "date_of_birth", "branch", 
        "department", "designation", "gender", "status"
    ]

    # 3. Logic for "Exit Employee" View
    if filters.parameter == "Exit Employee":
        # Add Exit-Specific Columns
        columns.extend([
            {"label": _("Relieving Date"), "fieldname": "relieving_date", "fieldtype": "Date", "width": 110},
            {"label": _("Reason for Leaving"), "fieldname": "reason_for_leaving", "fieldtype": "Small Text", "width": 200}
        ])

        # Fetch data including exit details
        exit_fields = standard_fields + ["relieving_date", "reason_for_leaving"]
        
        data = frappe.get_list(
            "Employee",
            filters={
                "company": filters.company,
                "status": ["in", ["Left", "Inactive", "Suspended"]]
            },
            fields=exit_fields,
            as_list=True
        )

        chart = get_exit_chart(filters)
        return columns, data, None, chart

    # 4. Logic for Standard View (Branch, Grade, etc.)
    else:
        try:
            from hrms.hr.report.employee_analytics.employee_analytics import (
                get_employees, get_parameters, get_chart_data
            )
            
            # Use the core logic to get filtered employees
            raw_data = get_employees(filters)
            
            # Since get_employees might return different fields, 
            # we re-query to ensure our custom column order is respected
            employee_names = [d[0] for d in raw_data] if raw_data else []
            
            data = frappe.get_list(
                "Employee",
                filters={"name": ["in", employee_names]},
                fields=standard_fields,
                as_list=True
            )

            raw_parameters = get_parameters(filters)
            chart = get_chart_data(raw_parameters, filters)
            
            return columns, data, None, chart
        
        except Exception as e:
            frappe.log_error(f"Employee Analytics Error: {str(e)}")
            return columns, [], None, None

def get_exit_chart(filters):
    employee = frappe.qb.DocType("Employee")
    exit_data = (
        frappe.qb.from_(employee)
        .select(employee.status, Count(employee.name))
        .where(employee.company == filters.company)
        .where(employee.status.isin(["Left", "Inactive", "Suspended"]))
        .groupby(employee.status)
    ).run()

    return {
        "data": {
            "labels": [_(d[0]) for d in exit_data],
            "datasets": [{"name": _("Status"), "values": [d[1] for d in exit_data]}]
        },
        "type": "donut",
        "height": 300
    }