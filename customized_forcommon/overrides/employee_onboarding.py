from hrms.hr.doctype.employee_onboarding.employee_onboarding import EmployeeOnboarding
import frappe
from frappe import _

class CustomEmployeeOnboarding(EmployeeOnboarding):
    def on_submit(self):
        # if `boarding_status` is the relevant field, set it to "In Process".
        self.db_set("boarding_status", "In Process")  # Assuming 'In Process' is a valid status for onboarding
        self.reload()

    