# Copyright (c) 2026, Guba Technology and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AttendanceCollectionLog(Document):
	def validate(self):
		if not self.is_new():
			frappe.throw("This document is a log and cannot be modified.")
			
	def on_trash(self):
		frappe.throw("Log records cannot be deleted.")
	pass
