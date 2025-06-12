# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_fullname


class LeavePlan(Document):
	def validate(self):
		self.fill_leave_planned_by()

	def fill_leave_planned_by(self):
		self.leave_planned_by = get_fullname(frappe.session.user)

