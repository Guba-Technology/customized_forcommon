# Copyright (c) 2026, Guba Technology and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _

class MaterialReceiptforTransfer(Document):
	def validate(self):
		if self.is_new():
			return  
		self.validate_quantity_equality()
	def validate_quantity_equality(self):
		if not self.reference_document:
			frappe.throw(_("Reference Stock Entry is required for validation."))

		source_entry = frappe.get_all("Stock Entry Detail", filters={"parent": self.reference_document}, fields=["qty as source_qty"])
		print(f"Reference document: {self.reference_document}, Source Entry: {source_entry}")
		source_qty_total = 0
		for d in source_entry:
			source_qty_total += flt(d.source_qty)

		received_qty_total = 0
		for d in self.items:
			received_qty_total += flt(d.qty)

		total_rejected = flt(self.total_rejected_quantity)
		total_processed = received_qty_total + total_rejected

		if abs(source_qty_total - total_processed) > 0.001:
			# print(f"Source Qty Total: {source_qty_total}, Received Qty Total: {received_qty_total}, Total Rejected: {total_rejected}, Total Processed: {total_processed}")
			frappe.throw(
				_("Quantity mismatch. <br> Original Stock Entry Total: {0} <br> Calculated Total: {1} (Received: {2} + Rejected: {3})")
				.format(
					source_qty_total, 
					total_processed, 
					received_qty_total, 
					total_rejected
				)
			)