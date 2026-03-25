from hrms.hr.doctype.employee_performance_feedback.employee_performance_feedback import EmployeePerformanceFeedback
import frappe
from frappe import _
from frappe.utils import flt


class CustomEmployeePerformanceFeedback(EmployeePerformanceFeedback):
    def set_total_score(self):
        total = 0
        for entry in self.feedback_ratings:
            score = flt(entry.custom_score)
            total += flt(score)

        self.total_score = flt(total, self.precision("total_score"))
