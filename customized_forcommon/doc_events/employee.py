import frappe
from frappe.utils import getdate, date_diff
from dateutil.relativedelta import relativedelta

def update_fuel_payment(doc, method):
    fuel_price = frappe.db.get_value("Company", doc.company, "custom_fuel_price")
    if doc.custom_allowed_fuel and doc.custom_allowed_fuel > 0 and fuel_price > 0:
        doc.custom_fuel_payment = doc.custom_allowed_fuel * fuel_price
    else:
        doc.custom_fuel_payment = 0

def calculate_severance_amount(doc, method):
    if not doc.relieving_date or not doc.date_of_joining or not doc.custom_apply_severance_pay:
        doc.custom_severance_pay_amount = 0
        return

    # Get HR Settings
    hr_settings = frappe.get_doc("HR Settings")
    starting_year = hr_settings.custom_severenace_pay_starting_year or 1
    first_year_severance_days = hr_settings.custom_first_year_severance_days or 0
    subsequent_year_severance_days = hr_settings.custom_subsequent_year_severance_days or 0
    salary_divisor_days = hr_settings.custom_salary_divisor_days or 0

    # Use Basic Salary
    basic_salary = doc.ctc or 0
    if basic_salary <= 0:
        doc.custom_severance_pay_amount = 0
        return

    if salary_divisor_days > 0:
        daily_wage = basic_salary / salary_divisor_days
    else:
        daily_wage = 0

    # Total service
    service = relativedelta(getdate(doc.relieving_date), getdate(doc.date_of_joining))

    full_years = service.years
    full_months = service.months
    remaining_days = service.days

    # 🚫 Not eligible yet
    if full_years < starting_year:
        doc.custom_severance_pay_amount = 0
        return

    # ✅ Full severance calculation (from year 1)
    if full_years <= 1:
        severance = daily_wage * first_year_severance_days
    else:
        severance = ( daily_wage * first_year_severance_days) + ((full_years - 1) * subsequent_year_severance_days * daily_wage)

        # Remaining months and days
        remaining_year_fraction = ((full_months / 12) + (remaining_days / 365) )
        severance += (remaining_year_fraction * subsequent_year_severance_days* daily_wage)

    doc.custom_severance_pay_amount = severance


def update_base_in_salary_structure_assignment(doc, method):
    if not doc.has_value_changed("ctc"):
        return

    ctc = doc.ctc or 0
    grade = doc.grade

    if ctc <= 0:
        return

    salary_structure_assignments = frappe.get_all(
        "Salary Structure Assignment",
        filters={
            "employee": doc.name,
            "docstatus": 1
        },
        pluck="name"
    )

    for assignment in salary_structure_assignments:
        frappe.db.set_value(
            "Salary Structure Assignment",
            assignment,
            {
                "base": ctc,
                "grade": grade
            },
            update_modified=False
        )

def create_employee_severance_amount_record(doc, method):
    emp_sev_docs = frappe.get_all(
        "Employee Severance Amount",
        filters={"employee": doc.employee},
        fields=["name"]
    )

    if not emp_sev_docs:
        new_emp_sev_doc = frappe.new_doc("Employee Severance Amount")
        new_emp_sev_doc.employee = doc.employee
        new_emp_sev_doc.insert()
        return

    # Record already exists, so check whether relevant fields changed
    if (
        not doc.has_value_changed("relieving_date")
        and not doc.has_value_changed("custom_severance_pay_amount")
    ):
        return

    frappe.db.set_value(
        "Employee Severance Amount",
        emp_sev_docs[0].name,
        {
            "relieving_date": doc.relieving_date,
            "severance_amount": doc.custom_severance_pay_amount
        }
    )

def add_employee_details_to_internal_work_history(doc, method):
    """
    Add the employee's current branch, designation, department and
    joining date to Internal Work History.

    If any of branch/designation/department changes, close the previous
    history row and create a new one.
    """

    # Required values
    if not doc.date_of_joining:
        return

    if not doc.branch and not doc.designation and not doc.department:
        return

    # Get existing history rows
    history = doc.get("internal_work_history") or []

    # If there is no history yet, create the first record
    if not history:
        doc.append("internal_work_history", {
            "branch": doc.branch,
            "designation": doc.designation,
            "department": doc.department,
            "from_date": doc.date_of_joining
        })
        return

    # Get the latest history record
    latest = history[-1]

    # Check whether the current details are different
    details_changed = (
        latest.branch != doc.branch
        or latest.designation != doc.designation
        or latest.department != doc.department
    )

    if not details_changed:
        return

    # Determine the date from which the new details become effective
    from_date = frappe.utils.getdate(frappe.utils.nowdate())

    # Close the previous history record
    latest.to_date = frappe.utils.add_days(from_date, -1)

    # Add the new history record
    doc.append("internal_work_history", {
        "branch": doc.branch,
        "designation": doc.designation,
        "department": doc.department,
        "from_date": from_date
    })