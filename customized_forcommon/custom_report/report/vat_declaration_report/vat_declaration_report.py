# Copyright (c) 2025, Guba Technology and contributors
# For license information, please see license.txt

import frappe
import datetime
from collections import defaultdict
from customized_forcommon.custom_report.my_utilities.get_company_info import GetCompanyInfo
from customized_forcommon.custom_report.my_utilities.get_last_day import GetLastDay


get_company_info = GetCompanyInfo()
to_next = 0

def get_fiscal_month_order(start_month, end_month):
    if start_month <= end_month:
        return list(range(start_month, end_month + 1))
    else:
     return list(range(start_month, 13)) + list(range(1, end_month + 1))
    # return list(range(start_month, 13)) + list(range(1, end_month + 1))

class VATDeclarationReport:
    def __init__(self, filters=None):
        
        self.filters = filters or {}
        vat_map = {"VAT": "vat", "Non VAT": "non_vat", "7.5 percent": "vat_75"}
        raw_vat_type = self.filters.get("vat_type")
        self.filters["vat_type"] = vat_map.get(raw_vat_type, raw_vat_type)
        self.filters.setdefault("vat_payable_account", get_company_info.get_vat_payable_account())
        self.filters.setdefault("vat_receivable_account", get_company_info.get_vat_receivable_account())
        self.vat_receivable_account = self.filters["vat_receivable_account"]
        self.fiscal_year_start, self.fiscal_year, self.fiscal_year_end = get_company_info.get_fiscal_year_start()
        self.vat_openning = get_company_info.get_vat_openning(self.filters.get("year") or self.fiscal_year)

    def execute(self):
        if not self.filters["vat_payable_account"]:
            frappe.throw(
                "VAT payable account not found. Please set it in <a href='/app/company/{0}'>{0}</a> under the <b>VAT Account</b> tab.".format(
                    get_company_info.Company
                )
            )
        columns = self.get_columns()
        data = self.get_data()
        summary = self.get_summary(data)
        return columns, data, None, None, summary

    def get_columns(self):
        return [
            {"label": "Month", "fieldname": "month", "fieldtype": "Int"},
            {"label": "Revenue", "fieldname": "revenue", "fieldtype": "Float"},
            {"label": "VAT 15%", "fieldname": "s_vat_15", "fieldtype": "Float"},
            {"label": "VAT 7.5%", "fieldname": "s_vat_75", "fieldtype": "Float"},
            {"label": "VAT Received", "fieldname": "vat_received", "fieldtype": "Float"},
            {"label": "Purchase", "fieldname": "purchase", "fieldtype": "Float"},
            {"label": "VAT 15%", "fieldname": "p_vat_15", "fieldtype": "Float"},
            {"label": "VAT 7.5%", "fieldname": "p_vat_75", "fieldtype": "Float"},
            {"label": "VAT Paid", "fieldname": "vat_paid", "fieldtype": "Float"},
            {"label": "This Month Payable", "fieldname": "payable", "fieldtype": "Float"},
            {"label": "BBF", "fieldname": "bbf", "fieldtype": "Float"},
            {"label": "To Next Month", "fieldname": "to_next_month", "fieldtype": "Float"},
        ]

    def get_data(self):
        monthly_data = defaultdict(lambda: {
            "month": 0, "revenue": 0, "s_vat_15": 0, "s_vat_75": 0,
            "vat_received": 0, "purchase": 0, "p_vat_15": 0, "p_vat_75": 0,
            "vat_paid": 0, "payable": 0, "bbf": 0, "to_next_month": 0
        })

        full_filters = self.build_vat_report_filters(ignore_month=True)
        sales_invoices = frappe.get_all("Sales Invoice", filters=full_filters, fields=["name", "custom_vat_date"])
        for si in sales_invoices:
            items = frappe.get_all("Sales Invoice Item", filters={"parent": si.name}, fields=["amount"])
            taxes = frappe.get_all("Sales Taxes and Charges", filters={"parent": si.name}, fields=["rate", "account_head"])
            total_amount = sum(item.amount for item in items)
            s_vat_15 = sum(t.rate for t in taxes if abs(t.rate) == 15 and t.account_head in [self.filters["vat_payable_account"], self.vat_receivable_account])
            s_vat_75 = sum(t.rate for t in taxes if abs(t.rate) == 7.5 and t.account_head in [self.filters["vat_payable_account"], self.vat_receivable_account])
            if self.filters["vat_type"] == "vat" and s_vat_15 == 0 and s_vat_75 == 0:
                continue
            elif self.filters["vat_type"] == "non_vat" and (s_vat_15 != 0 or s_vat_75 != 0):
                continue
            elif self.filters["vat_type"] == "vat_75" and s_vat_75 != 7.5:
                continue
            month = si.custom_vat_date.month if si.custom_vat_date else 0
            monthly_data[month]["month"] = month
            monthly_data[month]["revenue"] += total_amount
            monthly_data[month]["s_vat_15"] += total_amount * s_vat_15 / 100
            monthly_data[month]["s_vat_75"] += total_amount * s_vat_75 / 100

        purchase_invoices = frappe.get_all("Purchase Invoice", filters=full_filters, fields=["name", "custom_vat_date"])
        for pi in purchase_invoices:
            items = frappe.get_all("Purchase Invoice Item", filters={"parent": pi.name}, fields=["amount"])
            taxes = frappe.get_all("Purchase Taxes and Charges", filters={"parent": pi.name}, fields=["rate", "account_head"])
            total_amount = sum(item.amount for item in items)
            p_vat_15 = sum(t.rate for t in taxes if abs(t.rate) == 15 and t.account_head in [self.filters["vat_payable_account"], self.vat_receivable_account])
            p_vat_75 = sum(t.rate for t in taxes if abs(t.rate) == 7.5 and t.account_head in [self.filters["vat_payable_account"], self.vat_receivable_account])
            if self.filters["vat_type"] == "vat" and p_vat_15 == 0 and p_vat_75 == 0:
                continue
            elif self.filters["vat_type"] == "non_vat" and (p_vat_15 != 0 or p_vat_75 != 0):
                continue
            elif self.filters["vat_type"] == "vat_75" and p_vat_75 != 7.5:
                continue
            month = pi.custom_vat_date.month if pi.custom_vat_date else 0
            monthly_data[month]["month"] = month
            monthly_data[month]["purchase"] += total_amount
            monthly_data[month]["p_vat_15"] += total_amount * p_vat_15 / 100
            monthly_data[month]["p_vat_75"] += total_amount * p_vat_75 / 100
        
        start_month = self.fiscal_year_start.month
        end_month = self.fiscal_year_end.month
        month_order = get_fiscal_month_order(start_month, end_month)

        previous_to_next = self.vat_openning or 0
        print("month: ", month_order)
        for month in month_order:
            
            if month not in monthly_data:
                continue
            month_data = monthly_data[month]
            month_data["bbf"] = previous_to_next
            month_data["vat_received"] = month_data["s_vat_15"] + month_data["s_vat_75"]
            month_data["vat_paid"] = abs(month_data["p_vat_15"] + month_data["p_vat_75"])
            month_data["payable"] = month_data["vat_received"] - month_data["vat_paid"]
            month_data["to_next_month"] = month_data["payable"] + month_data["bbf"]
            previous_to_next = month_data["to_next_month"]
            global to_next
            to_next = month_data["to_next_month"]

        display_month = self.filters.get("month")
        if display_month:
            display_month = int(display_month)
            return [monthly_data[display_month]] if display_month in monthly_data else []

        return [monthly_data[m] for m in month_order if m in monthly_data]

    def build_vat_report_filters(self, ignore_month=False, ignore_vat_date=False):
        filters = {"docstatus": 0}

        fiscal_year = self.filters.get("year")
        month = self.filters.get("month")
        

        
        year_start, year_end = (
            GetLastDay.get_fiscal_year(fiscal_year) if fiscal_year else GetLastDay.get_fiscal_year(self.fiscal_year)
        )

        start_month = year_start.month 
        end_month = year_end.month
        start_day = year_start.day
        end_day = year_end.day

        
       

        
        if not ignore_month and month:
            month = int(month)
            year = year_end.year if month < start_month else year_start.year
            from_date = f"{year}-{month:02d}-{start_day if month == start_month else 1:02d}"
            to_date = f"{year}-{month:02d}-{end_day:02d}"
            filters["custom_vat_date"] = ["between", [from_date, to_date]]
            return filters

        # Default: full fiscal year range
        from_date = f"{year_start.year}-{start_month:02d}-{start_day:02d}"
        to_date = f"{year_end.year}-{end_month:02d}-{end_day:02d}"
        filters["custom_vat_date"] = ["between", [from_date, to_date]]
        return filters




    def get_summary(self, data):
        def safe_sum(field):
            return sum(row.get(field, 0) or 0 for row in data)

        return [
            {
                "label": "Total VAT Payable",
                "fieldname": "total_vat",
                "fieldtype": "Currency",
                "value": f"{safe_sum('vat_received') - safe_sum('vat_paid'):,.2f}"
            },
            {
                "label": "Total Sales VAT Received",
                "fieldname": "total_sales_vat_received",
                "fieldtype": "Currency",
                "value": f"{safe_sum('s_vat_15') + safe_sum('s_vat_75'):,.2f}"
            },
            {
                "label": "Total Purchase VAT Paid",
                "fieldname": "total_purchase_vat_paid",
                "fieldtype": "Currency",
                "value": f"{safe_sum('p_vat_15') + safe_sum('p_vat_75'):,.2f}"
            },
            {
                "label": "Total Revenue",
                "fieldname": "total_revenue",
                "fieldtype": "Currency",
                "value": f"{safe_sum('revenue'):,.2f}"
            },
            {
                "label": "Total Purchase",
                "fieldname": "total_purchase",
                "fieldtype": "Currency",
                "value": f"{safe_sum('purchase'):,.2f}"
            }
        ]
def execute(filters=None):
    return VATDeclarationReport(filters).execute()




@frappe.whitelist()
def update_vat_closing(year):
    company_name = frappe.defaults.get_user_default("Company")
    company = frappe.get_doc("Company", company_name)
   
    exist = False
    vc = frappe.db.get_value("VAT Closing", {"parent": company_name, "fiscal_year": year}, "name")
    if vc:
        exist = True
        vc_update = frappe.get_doc("VAT Closing", vc)
        vc_update.vat_closing = to_next
        vc_update.save()
    if not exist:
        vat_closing = frappe.new_doc("VAT Closing")
        vat_closing.parent = company_name
        vat_closing.parenttype = "Company"
        vat_closing.parentfield = "vat_closings"
        vat_closing.idx = 1
        vat_closing.vat_opening = company.custom_vat_openning_amount
        vat_closing.vat_closing = to_next
        vat_closing.fiscal_year = year
        vat_closing.save()

    return to_next

   