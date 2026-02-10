# Copyright (c) 2025, Guba Technology and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class MaxUserRestriction(Document):
	def validate(self):
		self.validate_max_users()

	def validate_max_users(self):
		if self.no_of_users_allowed < 0:
			frappe.throw("Number of users allowed cannot be negative")
		existed_restriction = frappe.get_all(
			"Max User Restriction",
			filters={"docstatus": 1, "name": self.name},
			fields=["name"]
		)
		if existed_restriction:
			frappe.throw(
				_("A Max User Restriction with this name already exists. Please use a different name."),
				title=_("Duplicate Max User Restriction")
			)


