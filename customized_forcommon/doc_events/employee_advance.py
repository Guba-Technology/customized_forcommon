import frappe
from frappe.utils import today, getdate, flt

# VALIDATIONS
def validate_payment_type(doc, method):
    if doc.repay_unclaimed_amount_from_salary != 1:
        return

    if doc.custom_repayment_type == "Fixed":
        doc.custom_fixed_repayment_amount_original = doc.custom_repayment_amount

    if doc.custom_repayment_type == "Number of Months":
        doc.custom_remaining_months = doc.custom_number_of_month
    
    clear_repayment_info(doc)
    validate_number_of_month(doc)
    validate_rate(doc)
    validate_repayment_amount(doc)
    validate_starting_payroll_date(doc)

def clear_repayment_info(doc):
    if doc.is_new():
        doc.set("custom_repayment_amount", 0)
        doc.set("custom_payroll_dates", [])

def validate_number_of_month(doc):
    if doc.custom_repayment_type == "Number of Months":
        if doc.custom_number_of_month < 1:
            frappe.throw("Number of Month must be at least 1")

def validate_rate(doc):
    if doc.custom_repayment_type == "Salary Percentage":
        if doc.custom_rate <= 0:
            frappe.throw("Rate must be greater than 0")

def validate_repayment_amount(doc):
    if doc.custom_repayment_type == "Fixed":
        if doc.custom_repayment_amount <= 0:
            frappe.throw("Repayment Amount must be greater than 0")

def validate_starting_payroll_date(doc):
    if doc.custom_repayment_type:
        if getdate(doc.custom_starting_payroll_date) < getdate(today()):
            frappe.throw("Starting Payroll Date cannot be in the past")

# CORE HELPERS
def get_remaining_amount(ea):
    remaining = flt(ea.paid_amount) - flt(ea.claimed_amount) - flt(ea.return_amount)
    return max(0, remaining)

def decrease_remaining_month(ea):
    if ea.custom_repayment_type == "Number of Months":
        if ea.custom_remaining_months > 0:
            ea.db_set("custom_remaining_months", ea.custom_remaining_months - 1)

def increase_remaining_month(ea):
    if ea.custom_repayment_type == "Number of Months":
        ea.db_set("custom_remaining_months", ea.custom_remaining_months + 1)

def update_repayment_amount(ea):
    remaining = get_remaining_amount(ea)

    if ea.custom_repayment_type == "Fixed":
        if remaining >= ea.custom_fixed_repayment_amount_original:
            repayment = ea.custom_fixed_repayment_amount_original
        else:
            repayment = remaining

    elif ea.custom_repayment_type == "Number of Months":
        months = flt(ea.custom_remaining_months)

        if months <= 0:
            repayment = remaining  # last payment
        else:
            repayment = flt(remaining / months)

    elif ea.custom_repayment_type == "Salary Percentage":
        employee_ctc = flt(frappe.db.get_value("Employee", ea.employee, "ctc"))
        rate = flt(ea.custom_rate)

        if not employee_ctc or not rate:
            return

        repayment = employee_ctc * rate / 100

        if repayment > remaining:
            repayment = remaining

    else:
        return

    ea.db_set("custom_repayment_amount", repayment)


# PAYMENT ENTRY (FIRST REPAYMENT)
def create_first_repayment_on_payment(doc, method):
    for ref in getattr(doc, "references", []):
        if ref.reference_doctype != "Employee Advance":
            continue

        ea = frappe.get_doc("Employee Advance", ref.reference_name)

        # already started → skip
        if ea.custom_payroll_dates:
            continue

        if not ea.repay_unclaimed_amount_from_salary:
            continue

        if getdate(ea.custom_starting_payroll_date) > getdate(today()):
            continue

        # capture months before any decrease
        initial_months = ea.custom_remaining_months
        # first repayment amount
        deduction = get_remaining_amount(ea) / initial_months
        if deduction <= 0:
            continue

        salary = frappe.new_doc("Additional Salary")
        salary.employee = ea.employee
        salary.company = ea.company
        salary.salary_component = ea.custom_salary_component
        salary.amount = deduction
        salary.currency = ea.currency
        salary.payroll_date = today()
        salary.overwrite_salary_structure_amount = 0
        salary.ref_doctype = "Employee Advance"
        salary.ref_docname = ea.name
        salary.custom_auto_created = 1

        salary.insert(ignore_permissions=True)
        salary.submit()

        frappe.db.commit()  # commit so claimed/return amounts are updated

        # reload EA to get updated claimed/return
        ea = frappe.get_doc("Employee Advance", ea.name)

        # add repayment row
        frappe.get_doc({
            "doctype": "Employee Advance Auto Repayment Dates",
            "parent": ea.name,
            "parenttype": "Employee Advance",
            "parentfield": "custom_payroll_dates",
            "payroll_date": today(),
            "repaid_amount": deduction,
            "reference": salary.name
        }).insert(ignore_permissions=True)

        # now decrease remaining months and recalc repayment for next scheduler
        decrease_remaining_month(ea)
        update_repayment_amount(ea)


def calculate_repayment_amount_during_payment_entry_cancellation(doc, method):
    for ref in doc.references:
        if ref.reference_doctype != "Employee Advance":
            continue

        ea = frappe.get_doc("Employee Advance", ref.reference_name)

        # find auto-created Additional Salary linked to this advance
        salaries = frappe.get_all(
            "Additional Salary",
            filters={
                "ref_doctype": "Employee Advance",
                "ref_docname": ea.name,
                "custom_auto_created": 1,
                "docstatus": 1  # submitted only
            },
            fields=["name"]
        )

        for sal in salaries:
            salary_doc = frappe.get_doc("Additional Salary", sal.name)

            # cancel safely
            if salary_doc.docstatus == 1:
                salary_doc.cancel()

        # AFTER cancellations → recalc safely
        update_repayment_amount(ea)

# ADDITIONAL SALARY
def calculate_repayment_amount_during_additional_salary_submission(doc, method):
    if getattr(doc, "ref_doctype", None) != "Employee Advance":
        return

    ea = frappe.get_doc("Employee Advance", doc.ref_docname)

    update_repayment_amount(ea)

def calculate_repayment_amount_during_additional_salary_cancellation(doc, method):
    if getattr(doc, "ref_doctype", None) != "Employee Advance":
        return

    ea = frappe.get_doc("Employee Advance", doc.ref_docname)
    if doc.custom_auto_created:
        increase_remaining_month(ea)
    update_repayment_amount(ea)

    # delete repayment row
    frappe.db.delete(
        "Employee Advance Auto Repayment Dates",
        {
            "parent": ea.name,
            "reference": doc.name,
        },
    )

# EXPENSE CLAIM
def calculate_repayment_amount_during_expense_claim(doc, method):
    for row in doc.get("advances", []):
        if not row.employee_advance:
            continue

        ea = frappe.get_doc("Employee Advance", row.employee_advance)

        update_repayment_amount(ea)
