# Copyright (c) 2025, Guba Technology and contributors
# For license information, please see license.txt

import frappe
import datetime
from customized_forcommon.custom_report.my_utilities.get_company_info import GetCompanyInfo
from customized_forcommon.custom_report.my_utilities.get_last_day import GetLastDay

get_company_info = GetCompanyInfo()

class VATSalesReport:
    def __init__(self, filters=None):
        self.filters = filters or {}
        self.filters["vat_type"] = self.filters.get("vat_type")  
        self.filters.setdefault("vat_payable_account", get_company_info.get_vat_payable_account())
        self.filters.setdefault("vat_recievable_account", get_company_info.get_vat_receivable_account)
        self.vat_re = get_company_info.get_vat_receivable_account()


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
            {"label": "Sales Invoice", "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice"},
            {"label": "VAT Category", "fieldname": "vat_category", "fieldtype": "Select", "options": "\ngoods\nservices"},
            {"label": "Type Of Sale", "fieldname": "type_of_sale", "fieldtype": "Select", "options": "Taxable Sale\nZero Rated Sale\nTax Exempted Sale"},
            {"label": "Buyer TIN", "fieldname": "buyer_tin", "fieldtype": "Data"},
            {"label": "Buyer Name", "fieldname": "buyer_name", "fieldtype": "Data"},
            {"label": "Date of Sale", "fieldname": "date_of_sale", "fieldtype": "Date"},
            {"label": "MRC Number", "fieldname": "mrc_number", "fieldtype": "Data"},
            {"label": "VAT Receipt Number", "fieldname": "vat_receipt_number", "fieldtype": "Data"},
            {"label": "Description", "fieldname": "description", "fieldtype": "Data"},
            {"label": "Unit of Measure", "fieldname": "unit_of_measure", "fieldtype": "Data"},
            {"label": "Quantity", "fieldname": "quantity", "fieldtype": "Float"},
            {"label": "Unit Price", "fieldname": "unit_price", "fieldtype": "Currency"},
            {"label": "Total Value", "fieldname": "total_value", "fieldtype": "Currency"},
            {"label": "VAT", "fieldname": "vat", "fieldtype": "Currency"},
            {"label": "VAT Receivable","fieldname":"vat_receivable","fieldtype":"Currency"},
            {"label": "VAT Payable","fieldname":"vat_payable","fieldtype":"Currency"},
            {"label": "Value After VAT", "fieldname": "value_after_vat", "fieldtype": "Currency"},
        ]

    def get_data(self):
        invoices = frappe.get_all("Sales Invoice",
            filters=self.build_sales_tax_filters(),
            fields=[
                "name", "custom_vat_category", "custom_type_of_sale", "tax_id",
                "customer_name", "posting_date", "custom_mrc_number",
                "custom_vat_receipt_number", "custom_description"
            ]
        )
        
        data = []
        for invoice in invoices:
            vat_payable = 0
            vat_receivable = 0
            items = frappe.get_all("Sales Invoice Item",
                filters={"parent": invoice.name},
                fields=["uom", "qty", "rate", "amount"]
            )
            
            taxes = frappe.get_all("Sales Taxes and Charges",
                filters={"parent": invoice.name, "account_head": self.filters["vat_payable_account"]} ,
                fields=["rate"]
            )
            vat_payable += sum(i.get("rate",0) for i in taxes)
            
            tax_half = frappe.get_all("Sales Taxes and Charges",
                filters={"parent": invoice.name, "account_head": self.vat_re},
                fields=["rate"])
            vat_receivable = sum(i.get("rate",0) for i in tax_half)
            
            vat_rate = vat_receivable + vat_payable
            if self.filters["vat_type"] == "VAT" and abs(vat_rate) == 0:
                continue
            elif self.filters["vat_type"] == "Non VAT" and vat_rate != 0:
                continue
            elif self.filters["vat_type"] == "7.5 percent" and abs(vat_rate) != 7.5:
                continue
            else:
                pass
            

            for item in items:
                
                receivable = item["amount"] * vat_receivable / 100 
                payable = item["amount"] * vat_payable / 100 
                vat = receivable + payable
                value_after_vat = item["amount"] - vat
                data.append({
                    "sales_invoice": invoice.name,
                    "vat_category": invoice.custom_vat_category,
                    "type_of_sale": invoice.custom_type_of_sale,
                    "buyer_tin": invoice.tax_id,
                    "buyer_name": invoice.customer_name,
                    "date_of_sale": invoice.posting_date,
                    "mrc_number": invoice.custom_mrc_number,
                    "vat_receipt_number": invoice.custom_vat_receipt_number,
                    "description": invoice.custom_description,
                    "unit_of_measure": item.uom,
                    "quantity": item.qty,
                    "unit_price": item.rate,
                    "total_value": item.amount,
                    "vat": vat,
                    "vat_payable": payable,
                    "vat_receivable":receivable, 
                    "value_after_vat": value_after_vat
                })
        return data

    def build_sales_tax_filters(self):
        filters =  {"docstatus":1}
        year = self.filters.get("year", datetime.date.today().year)
        month = self.filters.get("month")

        if month:
            lsd = GetLastDay(month)
            filters["posting_date"] = ["between", [
                f"{year}-{month}-01",
                f"{year}-{month}-{lsd.get_last_day()}"
            ]]
        elif self.filters.get("year"):
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
            # {"label": "Total Quantity", "fieldname": "total_quantity", "fieldtype": "Data", "value": f"{safe_sum('quantity'):,.2f}"},
            {"label": "Total Value", "fieldname": "total_value", "fieldtype": "Data", "value": f"{safe_sum('total_value'):,.2f}"},
            {"label": "Total VAT", "fieldname": "total_vat", "fieldtype": "Data", "value": f"{safe_sum('vat'):,.2f}"},
            {"label": "Total Value After VAT", "fieldname": "total_after_vat", "fieldtype": "Data", "value": f"{safe_sum('value_after_vat'):,.2f}"},
            {"label": "Vat Payable", "fieldname": "Total_vat_payable", "fieldtype": "Currency", "value": f"{safe_sum('vat_payable'):,.2f}"},
            {"label": "Vat Receivable", "fieldname": "Total_vat_receivable", "fieldtype": "Currency", "value": f"{safe_sum('vat_receivable'):,.2f}"}
        ]

def execute(filters=None):
    return VATSalesReport(filters).execute()
