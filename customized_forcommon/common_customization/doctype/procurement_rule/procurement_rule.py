# Copyright (c) 2026, Guba Technology
# License: MIT

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ProcurementRule(Document):
	def validate(self):
		if self.maximum_amount and flt(self.minimum_amount) > flt(self.maximum_amount):
			frappe.throw(frappe._("Minimum Amount cannot be greater than Maximum Amount."))
