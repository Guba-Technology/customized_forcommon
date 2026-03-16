import frappe
from frappe.utils import today, getdate, flt, add_months
def validate_payment_type(doc, method):
    if doc.repay_unclaimed_amount_from_salary != 1 :
        return
    if doc.custom_repayment_type == "Fixed":
        doc.custom_fixed_repayment_amount_original = doc.custom_repayment_amount
    validate_number_of_month(doc)
    validate_rate(doc)
    validate_repayment_amount(doc)
    validate_starting_payroll_date(doc)

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

def get_remaining_amount(ea):
    remaining = flt(ea.paid_amount) - flt(ea.claimed_amount) - flt(ea.return_amount)
    return max(0, remaining)

def update_repayment_amount(ea):
    remaining = get_remaining_amount(ea)
    if ea.custom_repayment_type == "Fixed":
        if remaining >= ea.custom_fixed_repayment_amount_original:
            repayment = ea.custom_fixed_repayment_amount_original
        else:
            repayment = remaining
    elif ea.custom_repayment_type == "Number of Months":
        months = flt(ea.custom_number_of_month)
        if not months:
            frappe.throw("Number of Months must be greater than 0")
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

def calculate_repayment_amount_during_payment_entry(doc, method):
    for ref in doc.references:
        if ref.reference_doctype != "Employee Advance":
            continue
        ea = frappe.get_doc("Employee Advance", ref.reference_name)
        update_repayment_amount(ea)
        
def calculate_repayment_amount_during_additional_salary_submission(doc, method):
    if getattr(doc, "ref_doctype", None) != "Employee Advance":
        return
    ea = frappe.get_doc("Employee Advance", doc.ref_docname)
    update_repayment_amount(ea)
    
def calculate_repayment_amount_during_additional_salary_cancellation(doc, method):
    if getattr(doc, "ref_doctype", None) != "Employee Advance":
        return
    ea = frappe.get_doc("Employee Advance", doc.ref_docname)
    update_repayment_amount(ea)
    # Delete the row linked to this Additional Salary
    frappe.db.delete(
        "Employee Advance Auto Repayment Dates",
        filters={
            "parent": ea.name,
            "parenttype": "Employee Advance",
            "parentfield": "custom_payroll_dates",
            "reference": doc.name,
        },
    )

def calculate_repayment_amount_during_expense_claim(doc, method):
    for row in doc.get("advances", []):
        if not row.advance:
            continue
        ea = frappe.get_doc("Employee Advance", row.advance)
        update_repayment_amount(ea)