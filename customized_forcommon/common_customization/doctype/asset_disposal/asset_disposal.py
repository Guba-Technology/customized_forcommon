# Copyright (c) 2025, guba and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AssetDisposal(Document):
	def validate(self):
		if self.disposal_type == "Sale":
			if not self.buyer_reciever:
				frappe.throw("Buyer/Receiver is required for Sale disposals.")
			if not self.salvage_value or self.salvage_value <= 0:
				frappe.throw("Salvage Value must be greater than zero for Sale.")
			if not self.approved_by:
				frappe.throw("Approval is required for Sale disposals.")

		elif self.disposal_type == "Write-off":
			if self.salvage_value:
				frappe.throw("Write-off disposals must not have a Salvage Value.")
			if self.buyer_reciever:
				frappe.throw("Write-off disposals cannot have a Buyer/Receiver.")
			if not self.approved_by:
				frappe.throw("Approval is required for Write-off disposals.")

		elif self.disposal_type == "Lost":
			if self.salvage_value or self.buyer_receiver:
				frappe.throw("Lost disposals must not have Salvage Value or Buyer.")
			# Approval optional

		elif self.disposal_type == "Scrap":
			if not self.approved_by:
				frappe.throw("Approval is required for Scrap disposals.")


	pass
@frappe.whitelist()
def calculate_gain_loss(doc, salvage_value):
	doc = frappe.get_doc("Asset", doc)
	d_schedule = frappe.get_all("Asset Depreciation Schedule",filters={"asset": doc.name}, fields=["expected_value_after_useful_life"])
	acc_d = 0
	
	gain_loss = 0
	nbv = 0
	for d1 in d_schedule:
		acc_d =  doc.gross_purchase_amount - d1.expected_value_after_useful_life
		nbv = doc.gross_purchase_amount - acc_d
		gain_loss =  float(salvage_value) - nbv

	return {
		"accumulated_depreciation": acc_d,
		"gain_loss": gain_loss,
	}
@frappe.whitelist()
def get_asset_data(doc):
	doc = frappe.get_doc("Asset", doc)
	return {
		"item_code": doc.item_code,
		"company": doc.company,
	}
	
