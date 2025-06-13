import frappe
from erpnext.setup.doctype.employee.employee import Employee
from frappe.utils import add_years, getdate, nowdate

class CustomEmployee(Employee):
    def validate(self):
        super().validate()
        # frappe.msgprint("CustomEmployee.validate triggered for CTC setting")
        self.set_ctc_from_grade_and_promotion()
        self.validate_18_years_old()

    def set_ctc_from_grade_and_promotion(self):
        """Set CTC from Employee Grade and Promotion if available."""

        # Check if the employee has a promotion and fetch the revised CTC
        promotion_list = frappe.get_list(
                "Employee Promotion",
                filters={
                    "employee": self.name,
                    "docstatus": 1
                },
                fields=["name"],
                order_by="creation desc"
            )

        if promotion_list:
            promotion = frappe.get_doc("Employee Promotion", promotion_list[0].name)
            

        # get the revised CTC from the latest promotion
        promotion_salary = promotion.revised_ctc if promotion else 0

        # Fetch the CTC from the Employee Grade
        grade = frappe.get_doc("Employee Grade", self.grade)
        default_salary = grade.custom_default_salary if grade else 0

        if grade and promotion:
            # If both grade and promotion exist, set CTC from the latest promotion

            self.ctc = promotion_salary
            frappe.msgprint(
                f"CTC set to {promotion_salary} from latest promotion: {promotion.name}.",
                alert=True
            )
        elif grade and not promotion:
            # If no promotion, set CTC from Employee Grade
            self.ctc = default_salary
            frappe.msgprint(
                f"CTC set to {default_salary} from Employee Grade: {self.grade}.",
                alert=True
            )
        
        else:
            frappe.msgprint(
                "No Employee Grade or Promotion found to set CTC.",
                alert=True
            )

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

