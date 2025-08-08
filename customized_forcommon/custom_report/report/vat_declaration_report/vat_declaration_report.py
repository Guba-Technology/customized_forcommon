# Copyright (c) 2025, Guba Technology and contributors
# For license information, please see license.txt

import frappe
import datetime
from customized_forcommon.custom_report.my_utilities.get_company_info import GetCompanyInfo
from customized_forcommon.custom_report.my_utilities.get_last_day import GetLastDay
get_company_info = GetCompanyInfo()
def execute(filters=None):
    ff = build_invoice_filters(filters) or {}
    columns = [
        {"label": "Withholdee TIN", "fieldname": "withholdee_tin", "fieldtype": "Data"},
        {"label": "Withholdee Name", "fieldname": "withholdee_name", "fieldtype": "Data"},
        {"label": "Reciept Number", "fieldname": "reciept_number", "fieldtype": "Data"},
        {"label": "Withhold Date", "fieldname": "withhold_date", "fieldtype": "Date"},
        {"label": "Total Taxable Amount", "fieldname": "total_taxable", "fieldtype": "Currency"},
        {"label": "Sales Tax Withheld", "fieldname": "tax_withheld", "fieldtype": "Currency"},
        {"label": "Total Payable Amount", "fieldname": "total_payable", "fieldtype": "Currency"},
        {"label": "Purchase Tax Withheld", "fieldname": "tax_withheld_amount", "fieldtype": "Currency"},
    ]

    conditions_si = "si.docstatus = %(docstatus)s"
    conditions_pi = "pi.docstatus = %(docstatus)s"
    # if filters.get("month") or filters.get("year"):
    #      conditions_pi += " AND pi.posting_date = %(posting_date)s"
    #      conditions_si += " AND si.posting_date = %(posting_date)s"

  
    query = f"""
        SELECT
            si.tax_id AS withholdee_tin,
            si.customer_name AS withholdee_name,
            si.custom_receipt_number AS reciept_number,
            si.custom_withhold_date AS withhold_date,
            si.total AS total_taxable,
            si.total_taxes_and_charges AS tax_withheld,
            si.grand_total AS total_payable,
            si.docstatus AS docstatus,
            NULL AS purchase_invoice,
            NULL AS total_taxable_amount,
            NULL AS tax_withheld_amount,
            NULL AS total_payable_amount
        FROM `tabSales Invoice` si
        WHERE {conditions_si}
        UNION ALL
        SELECT
            NULL AS withholdee_tin,
            NULL AS withholdee_name,
            NULL AS reciept_number,
            NULL AS withhold_date,
            NULL AS total_taxable,
            NULL AS tax_withheld,
            NULL AS total_payable,
            NULL AS docstatus,
            pi.name AS purchase_invoice,
            pi.total AS total_taxable_amount,
            pi.total_taxes_and_charges AS tax_withheld_amount,
            pi.grand_total AS total_payable_amount
        FROM `tabPurchase Invoice` pi
        WHERE {conditions_pi}
    """

    try:
        custom_vat_payable_account = get_company_info.get_vat_payable_account()
        custom_vat_receivable_account = get_company_info.get_vat_receivable_account()
        if custom_vat_payable_account or custom_vat_receivable_account:
             data = frappe.db.sql(query, ff, as_dict=True)
             sales_tax_total = sum(row["tax_withheld"] for row in data if row["tax_withheld"] is not None)
             purchase_tax_total = sum(row["tax_withheld_amount"] for row in data if row["tax_withheld_amount"] is not None)
             diff = sales_tax_total + purchase_tax_total
             diff_percent = abs((diff / sales_tax_total) * 100) if sales_tax_total else 0

             report_summary = [
                {"label": "Sales Tax", "value": "{:,.2f}".format(sales_tax_total), "indicator": "Green"},
                {"label": "Purchase Tax", "value": "{:,.2f}".format(purchase_tax_total), "indicator": "Red"},
                {"label": "Tax Difference", "value": "{:,.2f}".format(diff), "indicator": "Blue"},
                {"label": "Tax Difference %", "value": "{:,.2f}".format(diff_percent), "indicator": "Blue"},
            ]

             return columns, data, None, None, report_summary
        else:
             frappe.throw(
			"VAT payable account or VAT receivable account not found. Please set in <a href='/app/company/{0}'>{0}</a> <br> available at <b>VAT Account </b> tab".format(
				get_company_info.Company
			))
        
    except Exception as e:
        frappe.throw("No submitted sales invoice or purchase invoice record found.", title="Error")

def build_invoice_filters(filters):
        filters = {"docstatus": 1}
        if filters.get("month"):
            lsd =GetLastDay(filters['month'])
            filters["posting_date"] = ["between", [
				f"{filters['year'] if filters.get('year') else datetime.date.today().year}-{filters['month']}-01",
				f"{filters['year'] if filters.get('year') else datetime.date.today().year}-{filters['month']}-{lsd.get_last_day()}"
			]]
        if filters.get("year"):
            lsd = GetLastDay(filters['month'] if filters.get('month') else datetime.date.today().month)
            filters["posting_date"] = ["between", [
				f"{filters['year']}-{filters['month'] if filters.get('month') else '01'}-01",
				f"{filters['year'] }-{filters['month'] if filters.get('month') else '12'}-{lsd.get_last_day()}"
			]] 
       
        return filters

