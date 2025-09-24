import frappe
from frappe.utils import flt
from customized_forcommon.custom_report.my_utilities.get_company_info import GetCompanyInfo
from customized_forcommon.custom_report.my_utilities.get_last_day import GetLastDay
import datetime
get_company_info = GetCompanyInfo()
def get_salary_components(component_type):
    return frappe.get_all(
        "Salary Component",
        filters={"type": component_type},
        fields=["name", "salary_component", "is_tax_applicable","salary_component_abbr","type"],
    )

def get_columns(components, deductibles):
    base_columns = [
        {"label": "Employee", "fieldname": "employee_name", "fieldtype": "Link", "options": "Employee"},
        {"label": "Full Name", "fieldname": "full_name", "fieldtype": "Data"},
        {"label": "TIN", "fieldname": "employee_tin", "fieldtype": "Data"},
        {"label": "Pension ID", "fieldname": "pension_id", "fieldtype": "Data"},
        {"label": "Salary Slip Date", "fieldname": "posting_date", "fieldtype": "Date"},
        {"label": "Start Date", "fieldname": "start_date", "fieldtype": "Date"},
        {"label": "End Date", "fieldname": "end_date", "fieldtype": "Date"},
    ]

    dynamic_columns = [{"label": comp.salary_component+" ("+comp.salary_component_abbr+")", "fieldname": frappe.scrub(comp.name), "fieldtype": "Currency"} for comp in components]
    summary_columns = [
        {"label": ded.salary_component+" ("+ded.salary_component_abbr+")", "fieldname": frappe.scrub(ded.name), "fieldtype": "Currency"} for ded in deductibles
    ] + [
        {"label": "Other Taxable", "fieldname": "other_taxable", "fieldtype": "Currency"},
        {"label": "Taxable Total", "fieldname": "total_taxable", "fieldtype": "Currency"},
        {"label": "Total non-taxable", "fieldname": "total_non_taxable", "fieldtype": "Currency"},
        {"label": "Tax Withheld", "fieldname": "tax_withheld", "fieldtype": "Currency"},
        {"label": "Net Payable", "fieldname": "net_payable", "fieldtype": "Currency"},
        {"label": "Gross Payable", "fieldname": "gross_payable", "fieldtype": "Currency"},
    ]

    return base_columns + dynamic_columns + summary_columns

def process_salary_slip(slip, components, deductibles):
    employee = frappe.get_doc("Employee", slip.employee)
    row = {
        "employee_name": slip.employee,
        "full_name": slip.employee_name,
        "employee_tin": employee.get("custom_employee_tin"),
        "pension_id": employee.get("custom_pid"),
        "start_date": employee.get("date_of_joining"),
        "end_date": employee.get("relieving_date"),
        "net_payable": slip.net_pay,
        "gross_payable": slip.gross_pay,
        "posting_date": slip.posting_date,
        "total_taxable": 0,
        "tax_withheld": 0,
        "total_non_taxable": 0,
        "other_taxable": 0
    }

    for comp in components:
        row[frappe.scrub(comp.name)] = 0
    for ded in deductibles:
        row[frappe.scrub(ded.name)] = 0

    taxable, non_taxable = 0, 0
    for earning in slip.earnings:
        is_taxable = frappe.get_value("Salary Component", earning.salary_component, "is_tax_applicable")
        key = frappe.scrub(earning.salary_component)
        row[key] += flt(earning.amount)
        if is_taxable:
            if earning.salary_component.lower() == "transport allowance" or earning.salary_component.lower() == "ta" or earning.salary_component.lower() == "over time" or earning.salary_component.lower() == "ot":
                row["other_taxable"] += flt(earning.amount)
            else:
                row["total_taxable"] += flt(earning.amount)
                taxable += flt(earning.amount)
        else:
            row["total_non_taxable"] += flt(earning.amount)
            non_taxable += flt(earning.amount)

    for deduction in slip.deductions:
        key = frappe.scrub(deduction.salary_component)
        row[key] += flt(deduction.amount)
        if "tax" in deduction.salary_component.lower(): # Change this condition accordingly.
            #tax withheld is the sum of all tax deductions or taxable deductions or other deductions
            row["tax_withheld"] += flt(deduction.amount)

    return row, taxable, non_taxable

def execute(filters=None):
    filters = build_icome_tax_filters(filters) or {}
    components = get_salary_components("Earning")
    deductibles = get_salary_components("Deduction")
    columns = get_columns(components, deductibles)

    # slip_filters = {"docstatus": 1}
    # if filters.get("employee"):
    #     slip_filters["employee"] = filters["employee"]

    slips = frappe.get_all("Salary Slip", filters=filters, fields=["name", "employee", "employee_name", "start_date", "end_date", "net_pay", "gross_pay"], order_by="posting_date desc")
    data, taxable, non_taxable, net_pay, total_deduction = [], 0, 0, 0, 0

    for slip_meta in slips:
        slip = frappe.get_doc("Salary Slip", slip_meta.name)
        row, slip_taxable, slip_non_taxable = process_salary_slip(slip, components, deductibles)
        data.append(row)
        taxable += slip_taxable
        non_taxable += slip_non_taxable
        net_pay += flt(slip.net_pay)
        total_deduction += flt(slip.total_deduction)

    report_summary = [
        {"label": "Taxable", "value": "{:,.2f}".format(taxable), "indicator": "Green"},
        {"label": "Non Taxable", "value": "{:,.2f}".format(non_taxable), "indicator": "Red"},
        {"label": "Net Pay", "value": "{:,.2f}".format(net_pay), "indicator": "Green"},
        {"label": "Total Deduction", "value": "{:,.2f}".format(total_deduction), "indicator": "Red"},
    ]

    return columns, data, None, None, report_summary
def build_icome_tax_filters(filters):
    f = {"docstatus": 1}
    fiscal_year = filters.get("year")
    year_satrt, year_end = GetLastDay.get_fiscal_year(fiscal_year) if fiscal_year else GetLastDay.get_fiscal_year(None)
    month = filters.get("month")
    year = year_satrt.year
    if month:
            if int(month) < year_satrt.month:
                year = year_end.year
    if filters.get("employee"):
        f["employee"] = filters["employee"]
    if filters.get("month") :
        lsd = GetLastDay(month)
        f["posting_date"] = ["between", [
            f"{year}-{filters['month']}-01",
            f"{year}-{filters['month']}-{lsd.get_last_day()}"
        ]]
    elif filters.get("year"):
        month = filters.get("month") or datetime.date.today().month
        lsd = GetLastDay(month)
        f["posting_date"] = ["between", [
            f"{year_satrt}",
            f"{year_end}"
        ]]
    return f
