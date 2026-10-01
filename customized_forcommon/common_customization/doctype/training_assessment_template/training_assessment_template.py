# Copyright (c) 2026, Guba Technology
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document


class TrainingAssessmentTemplate(Document):
	def validate(self):
		self.validate_duplicate_criteria()

	def validate_duplicate_criteria(self):
		"""Prevent the same criteria text being listed twice in one template."""
		seen = set()
		for row in self.criteria:
			text = (row.criteria or "").strip().lower()
			if not text:
				frappe.throw(_("Row #{0}: Criteria cannot be empty").format(row.idx))
			if text in seen:
				frappe.throw(_("Row #{0}: Duplicate criteria '{1}'").format(row.idx, row.criteria))
			seen.add(text)
