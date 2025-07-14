import frappe
from frappe.utils import add_days, getdate

def set_custom_return_date(doc, method):
    if not doc.to_date or not doc.employee:
        return

    # Get the holiday list from the employee's company
    holiday_list = get_company_holiday_list(doc.employee)

    # Start from the next day after to_date
    next_date = add_days(doc.to_date, 1)

    # Skip holidays only
    while is_holiday(holiday_list, next_date):
        next_date = add_days(next_date, 1)

    # Set the custom return date
    doc.custom_return_date = next_date


def is_holiday(holiday_list_name, date):
    """
    Checks if the given date exists in the Holiday child table for the given holiday list.
    """
    if not holiday_list_name:
        return False

    return frappe.db.exists("Holiday", {
        "holiday_date": getdate(date),
        "parent": holiday_list_name
    })


def get_company_holiday_list(employee_id):
    """
    Retrieves the default holiday list from the company of the given employee.
    """
    company = frappe.db.get_value("Employee", employee_id, "company")
    if company:
        return frappe.db.get_value("Company", company, "default_holiday_list")
    return None
