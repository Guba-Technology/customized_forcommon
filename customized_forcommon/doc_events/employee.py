import frappe
from frappe.utils import getdate, date_diff

def calculate_severance_amount(doc, method):
    if not doc.relieving_date or not doc.date_of_joining or not doc.custom_apply_severance_pay:
        doc.custom_severance_pay_amount = 0
        return

    # Get HR Settings
    hr_settings = frappe.get_doc("HR Settings")
    starting_year = hr_settings.custom_severenace_pay_starting_year or 1

    # Use Basic Salary
    basic_salary = doc.ctc or 0
    if basic_salary <= 0:
        doc.custom_severance_amount = 0
        return

    daily_wage = basic_salary / 30

    # Total service
    total_days = date_diff(doc.relieving_date, doc.date_of_joining)
    full_years = int(total_days / 365)

    # 🚫 Not eligible yet
    if full_years < starting_year:
        doc.custom_severance_amount = 0
        return

    # ✅ Full severance calculation (from year 1)
    if full_years <= 1:
        severance = daily_wage * 30
    else:
        severance = (daily_wage * 30) + ((full_years - 1) * 10 * daily_wage)

    doc.custom_severance_pay_amount = severance