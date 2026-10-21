# Copyright (c) 2026, Guba Technology
# License: MIT

import frappe
from frappe.model.document import Document


class ProcurementSettings(Document):
	pass


def get_procurement_settings():
	"""Return the single Procurement Settings document, cached per request."""
	if not frappe.db.exists("DocType", "Procurement Settings"):
		return frappe._dict()
	return frappe.get_cached_doc("Procurement Settings")
