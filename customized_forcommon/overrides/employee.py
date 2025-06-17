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

        promotion_salary = None  # Initialize in case no promotion is found

        # Check if the employee has a promotion and fetch the revised CTC
        promotion_list = frappe.get_list(
            "Employee Promotion",
            filters={
                "employee": self.name,
                "docstatus": 1
            },
            fields=["name"],
            order_by="creation desc",
            limit_page_length=1
        )

        promotion = None
        if promotion_list:
            promotion = frappe.get_doc("Employee Promotion", promotion_list[0].name)
            promotion_salary = promotion.revised_ctc

        # Fetch the CTC from the Employee Grade
        grade = None
        default_salary = None
        if self.grade:
            grade = frappe.get_doc("Employee Grade", self.grade)
            default_salary = grade.custom_default_salary
             
        # If no promotion, set CTC from Employee Grade
        if grade and not promotion:
            self.ctc = default_salary
            frappe.msgprint(
                f"CTC set to {default_salary} from Employee Grade: {self.grade}.",
                alert=True
            )
        # If no grade but a promotion exists, set CTC from the latest promotion
        elif not grade and promotion:
            self.ctc = promotion_salary
            frappe.msgprint(
                f"CTC set to {promotion_salary} from latest promotion: {promotion.name}.",
                alert=True
            )
        elif grade and promotion:
            self.ctc = promotion_salary
            frappe.msgprint(
                f"CTC set to {promotion_salary} from latest promotion: {promotion.name}.",
                alert=True
            )
        # If neither grade nor promotion exists, show an alert
        elif not grade and not promotion:
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