import frappe
from erpnext.setup.doctype.employee.employee import Employee
from frappe.utils import add_years, getdate, nowdate

class CustomEmployee(Employee):
    def validate(self):
        super().validate()
        # frappe.msgprint("CustomEmployee.validate triggered for CTC setting")
        self.set_ctc_from_grade()
        self.validate_18_years_old()

    def set_ctc_from_grade(self):
        """Set CTC from Employee Grade if available."""
        # Check if the grade is set and fetch the CTC from Employee Grade
        if self.grade:
            frappe.msgprint(f"Grade selected: {self.grade}")
            try:
                # Fetch the Employee Grade document
                grade_doc = frappe.get_doc("Employee Grade", self.grade)
                # Check if the custom default salary is set and assign it to CTC
                if grade_doc.custom_default_salary:
                    self.ctc = grade_doc.custom_default_salary
                    frappe.msgprint(f"CTC set to {self.ctc} from Grade {self.grade}")
            except Exception as e:
                frappe.msgprint(f"Error fetching grade: {e}")

    def validate_18_years_old(self):
        """Validate if the employee is at least 18 years old."""
        if self.date_of_birth:
            todate = getdate(nowdate())
            dob = getdate(self.date_of_birth if self.date_of_birth else nowdate()) #
            age = (todate - dob).days // 365  # Calculate age in years
            if age < 18:
                frappe.throw(
                    frappe._("Employee must be at least 18 years old. Current age: {} years").format(age),
                )
                )

