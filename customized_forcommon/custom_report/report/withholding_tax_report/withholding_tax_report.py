import frappe
import datetime
from customized_forcommon.custom_report.my_utilities.get_company_info import GetCompanyInfo
from customized_forcommon.custom_report.my_utilities.get_last_day import GetLastDay

class WithholdingReport:
    def __init__(self, filters=None):
        self.raw_filters = filters or {}
        self.filters = self.build_invoice_filters()
        self.columns = self.get_columns()
        self.get_company_info = GetCompanyInfo()
        self.payable = self.get_company_info.get_withholding_payable_account()
        self.receivable = self.get_company_info.get_withholding_receivable_account()

    def run(self):
        if not (self.payable and self.receivable):
            self.throw_missing_account_error()

        sales_data, sales_total = [[], 0]
        purchase_data, purchase_total = [[], 0]
        withholding_type = self.raw_filters.get("filter_type")
        if withholding_type =="Sales Invoice":
            sales_data, sales_total = self.get_invoice_data("Sales Invoice", "sales")
        elif withholding_type == "Purchase Invoice":
            purchase_data, purchase_total = self.get_invoice_data("Purchase Invoice", "purchase")
        else:
            sales_data, sales_total = self.get_invoice_data("Sales Invoice", "sales")
            purchase_data, purchase_total = self.get_invoice_data("Purchase Invoice", "purchase")
       
        data = self.normalize_data(sales_data, purchase_data)
        summary = self.get_summary(sales_total, purchase_total)

        return self.columns, data, None, None, summary

    def throw_missing_account_error(self):
        frappe.throw(
            f"Withholding payable account or withholding receivable account not found. Please set in "
            f"<a href='/app/company/{self.get_company_info.Company}'>{self.get_company_info.Company}</a><br>"
            f"Available at <b>VAT Account</b> tab"
        )

    def get_columns(self):
        return [
            {"label": "Invoice", "fieldname": "invoice_name", "fieldtype": "Dynamic Link", "options": "voucher_type"},
            {"label": "Voucher Type", "fieldname": "voucher_type", "fieldtype": "Data", "hidden": 1},
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
         
        ]

    def build_invoice_filters(self):
        f = {}
        month = self.raw_filters.get("month")
        # year = self.raw_filters.get("year") or datetime.date.today().year
        fiscal_year = self.raw_filters.get("year")
        year_satrt, year_end = GetLastDay.get_fiscal_year(fiscal_year) if fiscal_year else GetLastDay.get_fiscal_year(None)
        month = self.raw_filters.get("month")
        withholding_date = self.raw_filters.get("withholding_date")
        from_date = self.raw_filters.get("from_date")
        to_date = self.raw_filters.get("to_date")
        
        year = year_satrt.year
        f['docstatus'] = 1
        if month:
            if int(month) < year_satrt.month:
                year = year_end.year
            lsd = GetLastDay(month)
            f["custom_withhold_date"] = ["between", [f"{year}-{month}-01",f"{year}-{month}-{lsd.get_last_day()}"]]
        elif self.raw_filters.get("year"):
            lsd = GetLastDay(month if month else datetime.date.today().month)
            f["custom_withhold_date"] = ["between", [
                f"{year_satrt.year}-{month if month else year_satrt.month}-01",
                f"{year_end.year}-{month if month else year_end.month}-{lsd.get_last_day()}"
            ]]
        if withholding_date:
            f["custom_withhold_date"] = ["between", [withholding_date, withholding_date]]
        if from_date:
            f["posting_date"] = ["between", [from_date, to_date]]
       

        vat_map = {"goods": "good", "services": "services"}
        if self.raw_filters.get("vat_category") in vat_map:
            f["custom_vat_category"] = vat_map[self.raw_filters["vat_category"]]

        return f

    def get_invoice_data(self, doctype, invoice_type):
        withholding_type = self.raw_filters.get("filter_type")
        if withholding_type =="Sales Invoice":
            doctype = "Sales Invoice"
            invoice_type = "sales"
        if withholding_type == "Purchase Invoice":
            doctype = "Purchase Invoice"
            invoice_type = "purchase"
        fields = self.get_invoice_fields(doctype)
        invoices = frappe.get_all(doctype, filters=self.filters, fields=fields)
        total_withheld = self.annotate_withholding(invoices, invoice_type)
        return invoices, total_withheld

    def get_invoice_fields(self, doctype):
        if doctype == "Sales Invoice":
            
            return [
                "name as invoice_name", "tax_id as withholdee_tin", "customer_name as withholdee_name",
                "custom_receipt_number as reciept_number", "custom_withhold_date as withhold_date"
                 
            ]
        if doctype == "Purchase Invoice":
            return [
                "name as invoice_name", "tax_id as withholdee_tin", "supplier_name as withholdee_name","custom_receipt_number as reciept_number",
                "custom_withhold_date as withhold_date"
               
            ]

    def annotate_withholding(self, invoices, invoice_type):
        total = 0
        table = "Sales Taxes and Charges" if invoice_type == "sales" else "Purchase Taxes and Charges"
        account_filter = [self.payable, self.receivable]
        
        for inv in invoices:
            inv.update({
                "receivable": 0, "payable": 0, "preceivable": 0, "ppayable": 0,
                "tax_withheld_amount": 0, "tax_withheld": 0
            })

            taxes = frappe.get_all(table, filters={"parent": inv.name, "account_head": ("in", account_filter)}, fields=["rate", "account_head", "tax_amount"])
            withheld_sum = 0

            for tax in taxes:
                head = tax["account_head"].lower()
                if self.payable.lower().startswith(head):
                    if invoice_type == "sales":
                        inv["payable"] = tax["tax_amount"]
                    else:
                        inv["ppayable"] = tax["tax_amount"]
                elif self.receivable.lower().startswith(head):
                    if invoice_type == "sales":
                        inv["receivable"] = tax["tax_amount"]
                    else:
                        inv["preceivable"] = tax["tax_amount"]

                withheld_sum += tax["tax_amount"]

            if invoice_type == "sales":
                inv["voucher_type"] = "Sales Invoice"
                inv["tax_withheld"] = withheld_sum
            else:
                inv["voucher_type"] = "Purchase Invoice"
                inv["tax_withheld_amount"] = withheld_sum

            total += withheld_sum

        return total

    def normalize_data(self, sales, purchase):
        sales_data = [{**row, "tax_withheld_amount": None, "ppayable": None, "preceivable": None,} for row in sales]
        purchase_data = [{**row,  "tax_withheld": None, "payable": None, "receivable": None} for row in purchase]
        return sales_data + purchase_data

    def get_summary(self, sales_total, purchase_total):
        diff = sales_total - purchase_total
        diff_percent = abs((diff / sales_total) * 100) if sales_total else 0
        return [
            {"label": "Sales Withhold", "value": f"{sales_total:,.2f}", "indicator": "Green"},
            {"label": "Purchase withhold", "value": f"{purchase_total:,.2f}", "indicator": "Red"},
            {"label": "Difference", "value": f"{diff:,.2f}", "indicator": "Blue"},
            {"label": "Difference %", "value": f"{diff_percent:,.2f}", "indicator": "Blue"},
        ]

def execute(filters=None):
    return WithholdingReport(filters).run()
