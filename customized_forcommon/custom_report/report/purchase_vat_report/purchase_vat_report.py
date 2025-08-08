# Copyright (c) 2025, Guba Technology and contributors
# For license information, please see license.txt

import frappe
import datetime
from customized_forcommon.custom_report.my_utilities.get_company_info import GetCompanyInfo
from customized_forcommon.custom_report.my_utilities.get_last_day import GetLastDay
get_company_info = GetCompanyInfo()
class VATPurchaseReport:
	def __init__(self, filters=None):
		self.filters = filters or {}
		self.filters.setdefault("vat_account", "VAT")
	def execute(self, filters=None):
		company_vat_receivable_account = get_company_info.get_vat_receivable_account()
		if company_vat_receivable_account:
			columns = self.get_columns()
			data = self.get_data()
			summary = self.get_summary(data)
			return columns, data, None, None, summary
		else:
			frappe.throw(
			"VAT payable account or VAT receivable account not found. Please set in <a href='/app/company/{0}'>{0}</a> <br> available at <b>VAT Account </b> tab".format(
				get_company_info.Company
			))
	def get_columns(self):
		return  [
				{"label": "Purchase Invoice", "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice"},
				{"label": "VAT Category", "fieldname": "vat_category", "fieldtype": "select", "options": "goods\nservices"},
				{"label": "Type Of Purchase", "fieldname": "type_of_purchase", "fieldtype": "select", "options": "Taxable-local Purchase of Capital Assets\nTaxable-imported Purchase of Capital Assets\nTaxable-local Purchase of Inputs\nTaxable-imported Purchase of Inputs\nTaxable-general Expense Inputs Purchase\nTax Exempted-purchase with no vat or uncollectible inputs"},
				{"label": "Seller TIN", "fieldname": "seller_tin", "fieldtype": "Data"},
				{"label": "Seller name", "fieldname": "seller_name", "fieldtype": "Data"},
				{"label":"Date of Purchase","fieldname":"date_of_Purchase","fieldtype":"Date"},
				{"label":"MRC Number","fieldname":"mrc_number","fieldtype":"Data"},
				{"label":"Vat receipt number","fieldname":"vat_receipt_number","fieldtype":"Data"},
				{"label":"Description","fieldname":"description","fieldtype":"Data"},
				{"label":"Unit of Measure","fieldname":"unit_of_measure","fieldtype":"Data"},
				{"label":"Quantity","fieldname":"quantity","fieldtype":"Float"},
				{"label":"Unit Price","fieldname":"unit_price","fieldtype":"Currency"},
				{"label":"Total value","fieldname":"total_value","fieldtype":"Currency"},
				{"label":"VAT","fieldname":"vat","fieldtype":"Currency"},
				{"label":"Value After VAT","fieldname":"value_after_vat","fieldtype":"Currency"},
           ]
	def get_data(self):
		invoices = frappe.get_list("Purchase Invoice", filters=self.build_invoice_filters(), fields=[
			"name", "custom_vat_category", "custom_type_of_purchase", "tax_id",
                "seller_name", "posting_date", "custom_mrc_number",
                "custom_vat_receipt_number", "custom_description"
		])

		data = []
		for invoice in invoices:
			items = frappe.get_all("Purchase Invoice Item",
				filters = {"parent": invoice.name},
				fields = ["uom", "qty", "rate", "amount"]
			)
			taxes = frappe.get_all("Purchase Taxes and Charges",
				filters={"parent": invoice.name, "account_head": ["like", f"{self.filters['vat_account']}%"]},
				fields=["rate"]
			)
			data.append({
				"sales_invoice": invoice.name,
				"vat_category": invoice.custom_vat_category,
				"type_of_purchase": invoice.custom_type_of_purchase,
				"seller_tin": invoice.tax_id,
				"seller_name": invoice.seller_name,
				"date_of_Purchase": invoice.posting_date,
				"mrc_number": invoice.custom_mrc_number,
				"vat_receipt_number": invoice.custom_vat_receipt_number,
				"description": invoice.custom_description,
			})
			for item in items:
				vat = item["amount"] * taxes[0]["rate"] / 100
				value_after_vat = item["amount"] - vat
				data[-1].update({
					"unit_of_measure": item["uom"],
					"quantity": item["qty"],
					"unit_price": item["rate"],
					"total_value": item["amount"],
					"vat": vat,
					"value_after_vat": value_after_vat
				})
		return data
	def build_invoice_filters(self):
		filters = {"docstatus": 1}
		if self.filters.get("month"):
			lsd =GetLastDay(self.filters['month'])
			filters["posting_date"] = ["between", [
				f"{self.filters['year'] if self.filters.get('year') else datetime.date.today().year}-{self.filters['month']}-01",
				f"{self.filters['year'] if self.filters.get('year') else datetime.date.today().year}-{self.filters['month']}-{lsd.get_last_day()}"
			]]
		if self.filters.get("year"):
			lsd = GetLastDay(self.filters['month'] if self.filters.get('month') else datetime.date.today().month)
			filters["posting_date"] = ["between", [
				f"{self.filters['year']}-{self.filters['month'] if self.filters.get('month') else '01'}-01",
				f"{self.filters['year'] }-{self.filters['month'] if self.filters.get('month') else '12'}-{lsd.get_last_day()}"
			]]
		vat_map = {"goods": "good", "services": "services"}
		if self.filters.get("vat_category") in vat_map:
			filters["custom_vat_category"] = vat_map[self.filters["vat_category"]]
		return filters
	def get_summary(self, data):
		def safe_sum(field):
			return sum(d.get(field, 0) or 0 for d in data)

		return [
			{"label": "Total Value", "fieldname": "total_value", "fieldtype": "Currency", "value": f"{safe_sum('total_value'):,.2f}"},
			{"label": "Total VAT", "fieldname": "total_vat", "fieldtype": "Currency", "value": f"{safe_sum('vat'):,.2f}"},
			{"label": "Total Value After VAT", "fieldname": "total_after_vat", "fieldtype": "Currency", "value": f"{safe_sum('value_after_vat'):,.2f}"},
		]
def execute(filters=None):
	return VATPurchaseReport(filters).execute()


