# Copyright (c) 2026, Guba Technology
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document


class ItemSpecificationTemplate(Document):
	def validate(self):
		self.calculate_total_points()
		self.validate_single_standard_template()

	def calculate_total_points(self):
		self.total_points = sum((row.merit_points or 0) for row in self.criteria)

	def validate_single_standard_template(self):
		"""Only one standard template is allowed per Item."""
		if not self.is_standard or not self.item:
			return
		existing = frappe.db.exists(
			"Item Specification Template",
			{
				"item": self.item,
				"is_standard": 1,
				"name": ["!=", self.name or ""],
			},
		)
		if existing:
			frappe.throw(
				_("A standard specification template already exists for Item {0}: {1}").format(
					self.item, existing
				)
			)
