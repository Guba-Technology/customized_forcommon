import frappe
import datetime
from customized_forcommon.custom_report.my_utilities.get_company_info import GetCompanyInfo
from customized_forcommon.custom_report.my_utilities.get_last_day import GetLastDay

get_company_info = GetCompanyInfo()

def execute(filters=None):
    filters = build_invoice_filters(filters)
    columns = [
        {"label": "Withholdee TIN", "fieldname": "withholdee_tin", "fieldtype": "Data"},
        {"label": "Withholdee Name", "fieldname": "withholdee_name", "fieldtype": "Data"},
        {"label": "Reciept Number", "fieldname": "reciept_number", "fieldtype": "Data"},
        {"label": "Withhold Date", "fieldname": "withhold_date", "fieldtype": "Date"},
        {"label": "Sales Tax Withheld", "fieldname": "tax_withheld", "fieldtype": "Currency"},
        {"label": "Purchase Tax Withheld", "fieldname": "tax_withheld_amount", "fieldtype": "Currency"},
        {"label": "Sales Withheld payable", "fieldname": "payable", "fieldtype": "Currency"},
        {"label": "Sales withheld receivable", "fieldname": "receivable", "fieldtype": "Currency"},
        {"label": "Purchase Withheld payable", "fieldname": "ppayable", "fieldtype": "Currency"},
        {"label": "Purchase withheld receivable", "fieldname": "preceivable", "fieldtype": "Currency"},
        {"label": "Purchase Withheld", "fieldname": "purchase_withhold", "fieldtype": "Currency"},
    ]

    payable = get_company_info.get_withholding_payable_account()
    receivable = get_company_info.get_withholding_receivable_account()
    if not (payable and receivable):
        frappe.throw(
            f"Withholding payable account or withholding receivable account not found. Please set in <a href='/app/company/{get_company_info.Company}'>{get_company_info.Company}</a> <br> available at <b>VAT Account</b> tab"
        )
    sales_withhold = 0
    purchase_withhold = 0
    sales_invoices = frappe.get_all("Sales Invoice",
        filters=filters,
        fields=[
             "name",
            "tax_id as withholdee_tin",
            "customer_name as withholdee_name",
            "custom_receipt_number as reciept_number",
            "custom_withhold_date as withhold_date",
            "total_taxes_and_charges as tax_withheld",
            "total_qty as receivable",
            "base_net_total as payable"
        ]
    )
    
    sales_withhold = get_withhold(sales_invoices,"sales",payable,receivable)
    purchase_invoices = frappe.get_all("Purchase Invoice",
        filters=filters,
        fields=[
            "name",
            "tax_id as withholdee_tin",
            "supplier_name as withholdee_name",
            
            "total_taxes_and_charges as tax_withheld_amount",
            "total_qty as preceivable",
            "base_net_total as ppayable",
            "total_advance as purchase_withhold"
        ]
    )
    purchase_withhold = get_withhold(purchase_invoices,"purchase",payable,receivable)

    # Normalize union structure
    sales_data = [
        {**row, "tax_withheld_amount": None} for row in sales_invoices
    ]
    purchase_data = [
        {**row, "withholdee_tin": None, "withholdee_name": None, "reciept_number": None, "withhold_date": None, "tax_withheld": None} for row in purchase_invoices
    ]

    data = sales_data + purchase_data

    sales_tax_total = sales_withhold
    purchase_tax_total = purchase_withhold
    diff = sales_tax_total - purchase_tax_total
    diff_percent = abs((diff / sales_tax_total) * 100) if sales_tax_total else 0

    report_summary = [
        {"label": "Sales Withhold", "value": "{:,.2f}".format(sales_tax_total), "indicator": "Green"},
        {"label": "Purchase withhold", "value": "{:,.2f}".format(purchase_tax_total), "indicator": "Red"},
        {"label": "Difference", "value": "{:,.2f}".format(diff), "indicator": "Blue"},
        {"label": "Difference %", "value": "{:,.2f}".format(diff_percent), "indicator": "Blue"},
    ]

    return columns, data, None, None, report_summary
def get_withhold(data,type,payable,receivable):
    sales_withhold = 0
    
    for invoice in data:
        invoice["receivable"] = 0 
        invoice["payable"] = 0 
        invoice["preceivable"] = 0
        invoice["ppayable"] = 0
        invoice["purchase_withhold"] = 0
        invoice["tax_withheld_amount"] = 0
        table = "Sales Taxes and Charges" if type =="sales" else "Purchase Taxes and Charges"
        acc = payable if type == "sales" else receivable
        # taxes = frappe.db.sql("SELECT rate, account_head, tax_amount FROM `tabSales Taxes and Charges` WHERE account_head LIKE %s AND parent = %s", ("%vat%", invoice.name), as_dict=True)
        taxes = frappe.get_all(table,
                                filters={"parent": invoice.name, "account_head": ["like", acc]},
                                fields=["rate", "account_head", "tax_amount"])

        swh = sum(tax["tax_amount"] for tax in taxes)
        for tax in taxes:
            if "pay" in tax["account_head"].lower():
                invoice["payable"] = tax["tax_amount"] if type == "sales" else 0
                invoice["ppayable"] = tax["tax_amount"] if type == "purchase" else 0
            elif "receiv" in tax["account_head"].lower():
                invoice["receivable"] = tax["tax_amount"] if type == "sales" else 0
                invoice["preceivable"] = tax["tax_amount"] if type == "purchase" else 0

        invoice["tax_withheld"] = swh if type == "sales" else 0
        invoice["purchase_withhold"] = swh if type == "purchase" else 0
        sales_withhold += swh
        
    return sales_withhold

def build_invoice_filters(filters):
    filters = filters or {}
    f = {}

    if filters.get("month"):
        lsd = GetLastDay(filters["month"])
        year = filters.get("year") or datetime.date.today().year
        f["posting_date"] = ["between", [
            f"{year}-{filters['month']}-01",
            f"{year}-{filters['month']}-{lsd.get_last_day()}"
        ]]
    elif filters.get("year"):
        month = filters.get("month") or datetime.date.today().month
        lsd = GetLastDay(month)
        f["posting_date"] = ["between", [
            f"{filters['year']}-{month}-01",
            f"{filters['year']}-{month}-{lsd.get_last_day()}"
        ]]

    vat_map = {"goods": "good", "services": "services"}
    if filters.get("vat_category") in vat_map:
        f["custom_vat_category"] = vat_map[filters["vat_category"]]

    return f
