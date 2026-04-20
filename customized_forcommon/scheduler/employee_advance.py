import frappe
from frappe.utils import getdate, add_months, today, flt, get_first_day, get_last_day
from customized_forcommon.doc_events.employee_advance import update_repayment_amount

def process_repayments():
    """
    Scheduler:
    - Uses pre-calculated `custom_repayment_amount`
    - First repayment handled in Payment Entry
    - Scheduler handles subsequent repayments
    """
    advances = frappe.get_all(
        "Employee Advance",
        filters={
            "docstatus": 1,
            "status": "Paid",
            "repay_unclaimed_amount_from_salary": 1,
        },
        fields=["name", "custom_repayment_type"],
    )

    for adv_row in advances:
        adv = frappe.get_doc("Employee Advance", adv_row.name)

        # Remaining amount
        remaining = flt(adv.paid_amount) - flt(adv.claimed_amount) - flt(adv.return_amount)
        if remaining <= 0:
            continue

        next_date = get_next_payroll_date(adv)

        # Skip if not yet time
        if getdate(today()) < next_date:
            continue

        # Use already calculated repayment amount
        if adv.custom_repayment_type == "Salary Percentage":
            deduction = min(flt(adv.custom_next_repayment_amount), remaining)
        else:
            deduction = min(flt(adv.custom_repayment_amount), remaining)
        if deduction <= 0:
            continue

        try:
            salary = create_additional_salary(adv, deduction, next_date)
        except frappe.ValidationError:
            frappe.log_error(
                title=f"Failed Additional Salary: {adv.name}",
                message=f"Could not create Additional Salary on {next_date} for {adv.name}",
            )
            continue

        # Add repayment tracking row
        frappe.get_doc({
            "doctype": "Employee Advance Auto Repayment Dates",
            "parent": adv.name,
            "parenttype": "Employee Advance",
            "parentfield": "custom_payroll_dates",
            "payroll_date": next_date,
            "repaid_amount": deduction,
            "reference": salary.name,
        }).insert(ignore_permissions=True)

        # 1. Commit first → ensures claimed_amount is updated
        frappe.db.commit()

        # 2. Reload updated doc
        adv = frappe.get_doc("Employee Advance", adv.name)

        # 3. Decrease remaining months AFTER commit
        if adv.custom_repayment_type == "Number of Months" and adv.custom_remaining_months > 0:
            adv.db_set("custom_remaining_months", adv.custom_remaining_months - 1)

        # 4. Update repayment amount for NEXT cycle
        update_repayment_amount(adv)

        # 5. Commit again (safe persistence)
        frappe.db.commit()


def get_next_payroll_date(adv):
    today_date = getdate(today())

    if not adv.custom_payroll_dates:
        start_date = getdate(adv.custom_starting_payroll_date)

        first_day = get_first_day(today_date)
        last_day = get_last_day(today_date)

        if first_day <= start_date <= last_day:
            return today_date
        else:
            return start_date

    last_row = adv.custom_payroll_dates[-1]
    return add_months(getdate(last_row.payroll_date), 1)


def create_additional_salary(adv, amount, payroll_date):
    salary = frappe.new_doc("Additional Salary")
    salary.employee = adv.employee
    salary.company = adv.company
    salary.salary_component = adv.custom_salary_component
    salary.amount = amount
    salary.currency = adv.currency
    salary.payroll_date = payroll_date
    salary.overwrite_salary_structure_amount = 0
    salary.ref_doctype = "Employee Advance"
    salary.ref_docname = adv.name
    salary.custom_auto_created = 1

    salary.insert(ignore_permissions=True)
    salary.submit()

    return salary