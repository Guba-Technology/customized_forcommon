# Copyright (c) 2025, Guba Technology and contributors
# For license information, please see license.txt

import frappe
import datetime
from customized_forcommon.custom_report.my_utilities.get_company_info import GetCompanyInfo
from customized_forcommon.custom_report.my_utilities.get_last_day import GetLastDay

get_company_info = GetCompanyInfo()

class VATDeclarationReport:
    def __init__(self, filters=None):
        self.filters = filters or {}
        self.filters["vat_type"] = self.filters.get("vat_type")
        self.filters.setdefault("vat_payable_account", get_company_info.get_vat_payable_account())
        self.filters.setdefault("vat_receivable_account", get_company_info.get_vat_receivable_account())
        self.vat_receivable_account = self.filters["vat_receivable_account"]

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
            {"label": "Date", "fieldname": "date", "fieldtype": "Date"},
            {"label": "Voucher Type", "fieldname": "voucher_type", "fieldtype": "Data"},
            {"label": "Voucher Number", "fieldname": "voucher_number", "fieldtype": "Link", "options": "Sales Invoice"},
            {"label": "VAT Category", "fieldname": "vat_category", "fieldtype": "Select", "options": "\ngoods\nservices"},
            {"label": "Type Of Sale", "fieldname": "type_of_sale", "fieldtype": "Select", "options": "Taxable Sale\nZero Rated Sale\nTax Exempted Sale"},
            {"label": "Sales VAT", "fieldname": "vat", "fieldtype": "Currency"},
            {"label": "Sales VAT Receivable", "fieldname": "vat_receivable", "fieldtype": "Currency"},
            {"label": "Sales VAT Payable", "fieldname": "vat_payable", "fieldtype": "Currency"},
            {"label": "Purchase VAT", "fieldname": "purchase_vat", "fieldtype": "Currency"},
            {"label": "Purchase VAT Receivable", "fieldname": "purchase_vat_receivable", "fieldtype": "Currency"},
            {"label": "Purchase VAT Payable", "fieldname": "purchase_vat_payable", "fieldtype": "Currency"},
        ]

    def get_data(self):
        data = []

        # Process Sales Invoices
        sales_invoices = frappe.get_all("Sales Invoice",
            filters=self.build_sales_tax_filters(),
            fields=["name", "custom_vat_category", "custom_type_of_sale", "posting_date"]
        )

        for si in sales_invoices:
            items = frappe.get_all("Sales Invoice Item", filters={"parent": si.name}, fields=["amount"])
            taxes = frappe.get_all("Sales Taxes and Charges", filters={"parent": si.name}, fields=["rate", "account_head"])

            vat_receivable = sum(t.rate for t in taxes if t.account_head == self.vat_receivable_account)
            vat_payable = sum(t.rate for t in taxes if t.account_head == self.filters["vat_payable_account"])
            vat_total_rate = vat_receivable + vat_payable

            if self.filters["vat_type"] == "VAT" and vat_total_rate == 0:
                continue
            elif self.filters["vat_type"] == "Non VAT" and vat_total_rate != 0:
                continue
            elif self.filters["vat_type"] == "7.5 percent" and vat_total_rate != 7.5:
                continue

            for item in items:
                receivable = item.amount * vat_receivable / 100
                payable = item.amount * vat_payable / 100
                vat = receivable + payable

                data.append({
                    "date": si.posting_date,
                    "voucher_type": "Sales Invoice",
                    "voucher_number": si.name,
                    "vat_category": si.custom_vat_category,
                    "type_of_sale": si.custom_type_of_sale,
                    "vat": vat,
                    "vat_receivable": receivable,
                    "vat_payable": payable,
                    "purchase_vat": 0,
                    "purchase_vat_receivable": 0,
                    "purchase_vat_payable": 0,
                })

        # Process Purchase Invoices
        purchase_invoices = frappe.get_all("Purchase Invoice",
            filters=self.build_purchase_tax_filters(),
            fields=["name", "custom_vat_category", "posting_date"]
        )

        for pi in purchase_invoices:
            items = frappe.get_all("Purchase Invoice Item", filters={"parent": pi.name}, fields=["amount"])
            taxes = frappe.get_all("Purchase Taxes and Charges", filters={"parent": pi.name}, fields=["rate", "account_head"])

            vat_receivable = sum(t.rate for t in taxes if t.account_head == self.vat_receivable_account)
            vat_payable = sum(t.rate for t in taxes if t.account_head == self.filters["vat_payable_account"])
            vat_total_rate = vat_receivable + vat_payable
            
            if self.filters["vat_type"] == "VAT" and vat_total_rate == 0:
                continue
            elif self.filters["vat_type"] == "Non VAT" and vat_total_rate != 0:
                continue
            elif self.filters["vat_type"] == "7.5 percent" and vat_total_rate != 7.5:
                continue

            for item in items:
                receivable = item.amount * vat_receivable / 100
                payable = item.amount * vat_payable / 100
                vat = receivable + payable

                data.append({
                    "date": pi.posting_date,
                    "voucher_type": "Purchase Invoice",
                    "voucher_number": pi.name,
                    "vat_category": pi.custom_vat_category,
                    "type_of_sale": "",
                    "vat": 0,
                    "vat_receivable": 0,
                    "vat_payable": 0,
                    "purchase_vat": vat,
                    "purchase_vat_receivable": receivable,
                    "purchase_vat_payable": payable,
                })

        return data

    def build_sales_tax_filters(self):
        filters = {"docstatus": 1}
        year = self.filters.get("year", datetime.date.today().year)
        month = self.filters.get("month")
        lsd = GetLastDay(month if month else datetime.date.today().month)

        filters["posting_date"] = ["between", [
            f"{year}-{month if month else '01'}-01",
            f"{year}-{month if month else '12'}-{lsd.get_last_day()}"
        ]]

        vat_map = {"goods": "good", "services": "services"}
        if self.filters.get("vat_category") in vat_map:
            filters["custom_vat_category"] = vat_map[self.filters["vat_category"]]

        return filters

    def build_purchase_tax_filters(self):
        filters = {"docstatus": 1}
        year = self.filters.get("year", datetime.date.today().year)
        month = self.filters.get("month")
        lsd = GetLastDay(month if month else datetime.date.today().month)

        filters["posting_date"] = ["between", [
            f"{year}-{month if month else '01'}-01",
            f"{year}-{month if month else '12'}-{lsd.get_last_day()}"
        ]]

        vat_map = {"goods": "good", "services": "services"}
        if self.filters.get("vat_category") in vat_map:
            filters["custom_vat_category"] = vat_map[self.filters["vat_category"]]

        return filters

    def get_summary(self, data):
        def safe_sum(field):
            return sum(row.get(field, 0) or 0 for row in data)

        return [
            {"label": "Total VAT", "fieldname": "total_vat", "fieldtype": "Currency", "value": f"{safe_sum('vat'):,.2f}"},
            {"label": "Total Sales VAT Payable", "fieldname": "total_sales_vat_payable", "fieldtype": "Currency", "value": f"{safe_sum('vat_payable'):,.2f}"},
            {"label": "Total Sales VAT Receivable", "fieldname": "total_sales_vat_receivable", "fieldtype": "Currency", "value": f"{safe_sum('vat_receivable'):,.2f}"},
            {"label": "Total Purchase VAT Payable", "fieldname": "total_purchase_vat_payable", "fieldtype": "Currency", "value": f"{safe_sum('purchase_vat_payable'):,.2f}"},
            {"label": "Total Purchase VAT Receivable", "fieldname": "total_purchase_vat_receivable", "fieldtype": "Currency", "value": f"{safe_sum('purchase_vat_receivable'):,.2f}"},
        ]

def execute(filters=None):
    return VATDeclarationReport(filters).execute()
