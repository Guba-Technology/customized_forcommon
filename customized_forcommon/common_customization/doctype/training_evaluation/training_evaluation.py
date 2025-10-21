# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime


class TrainingEvaluation(Document):
	pass

@frappe.whitelist()
def get_training_event(training_event):
    te = frappe.get_doc("Training Event", training_event)
    start_time = te.start_time
    end_time = te.end_time

    if not start_time or not end_time:
        frappe.throw("Start time or end time is missing.")

    duration = end_time - start_time
    total_seconds = int(duration.total_seconds())

    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days:
        parts.append(f"{days} day{'s' if days > 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    if seconds:
        parts.append(f"{seconds} second{'s' if seconds > 1 else ''}")

    return ", ".join(parts) if parts else ''
@frappe.whitelist()
def grievance_auto_complete(raised_by):
	if raised_by:
          emp = frappe.get_doc("Employee", raised_by)
          return {
          "grade": emp.grade,
		  "company": emp.company,
        "address": emp.current_address
	}
