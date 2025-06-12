# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ItemSupply(Document):
	def validate(self):
		self.check_duplicate_items()

	def check_duplicate_items(self):
		items_list = set()
		if self.items:
			for row in self.items:
				if row.item:
					if row.item in items_list:
						frappe.throw(f"Duplicate Item {row.item} found in Items Table")
					items_list.add(row.item)
