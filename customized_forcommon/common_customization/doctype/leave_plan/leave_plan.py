# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_fullname
from frappe.utils.data import getdate
from datetime import datetime
import calendar

class LeavePlan(Document):
	def validate(self):
		self.fill_leave_planned_by()
		self.clear_leave_days()
		self.calculate_total_leave_days()
		


	def fill_leave_planned_by(self):
		self.leave_planned_by = get_fullname(frappe.session.user)

	def clear_leave_days(self):
		for i in range(1, 4):
			month_field = f"month{i}"
			days_field = f"month{i}_leave_days"
			if not getattr(self, month_field):
				setattr(self, days_field, None)
				
	def calculate_total_leave_days(self):
		if self.month1_leave_days and not self.month2_leave_days and not self.month3_leave_days:
			self.total_leave_days = self.month1_leave_days
		elif self.month1_leave_days and self.month2_leave_days and not self.month3_leave_days:
			self.total_leave_days = self.month1_leave_days + self.month2_leave_days
		elif self.month1_leave_days and self.month2_leave_days and self.month3_leave_days:
			self.total_leave_days = self.month1_leave_days + self.month2_leave_days + self.month3_leave_days
		elif self.month1_leave_days and not self.month2_leave_days and self.month3_leave_days:
			self.total_leave_days = self.month1_leave_days + self.month3_leave_days

	
		

