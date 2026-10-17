# Copyright (c) 2026, Guba Technology
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class TenderBiddingSettings(Document):
	def validate(self):
		spec_weight = flt(self.spec_weight_percent)
		price_weight = flt(self.price_weight_percent)
		if spec_weight + price_weight != 100:
			frappe.throw(_("Specification Weight % and Price Weight % must add up to 100."))

		if flt(self.minimum_spec_score) < 0 or flt(self.minimum_spec_score) > 100:
			frappe.throw(_("Minimum Specification Score % must be between 0 and 100."))


def get_settings():
	return frappe.get_cached_doc("Tender Bidding Settings")
