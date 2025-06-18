# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ClearanceTemplate(Document):
	def validate(self):
		self.validate_no_duplicate()

	def validate_no_duplicate(self):
		if self.clearance_template_table:
			# Check for duplicate entries in the clearance_template_table
			unique_entries = set()
			for entry in self.clearance_template_table:
				if entry.department in unique_entries:
					frappe.throw(
						_("Duplicate department {0} found in clearance template table.").format(entry.department)
					)
				unique_entries.add(entry.department)
