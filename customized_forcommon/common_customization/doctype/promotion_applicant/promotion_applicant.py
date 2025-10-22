# Copyright (c) 2025, Guba Technology and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class PromotionApplicant(Document):
	def before_submit(self):
		if self.status =="" or self.status == None:
			self.status = "Pending"
	pass
