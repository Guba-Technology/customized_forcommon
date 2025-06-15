import frappe
from hrms.hr.doctype.employee_promotion.employee_promotion import EmployeePromotion

class CustomEmployeePromotion(EmployeePromotion):
    def validate(self):
        super().validate()
        self.set_revised_ctc_from_grade()

    def set_revised_ctc_from_grade(self):
        grade_found = False

        # loop through promotion_details to find the Grade
        for row in self.promotion_details:
            # Check if the property is "Grade" and if a new value is set
            if row.property == "Grade" and row.new:
                try:
                    grade_current = frappe.get_doc("Employee Grade", row.current)
                    grade_new = frappe.get_doc("Employee Grade", row.new)

                    # If the new Grade has a custom default salary greater than the current Grade's custom default salary,
                    # set it as revised_ctc, otherwise keep the current Grade's custom default salary
                    if grade_new.custom_default_salary > grade_current.custom_default_salary:
                        self.revised_ctc = grade_new.custom_default_salary
                        grade_found = True
                        break
                    else:
                        self.revised_ctc = grade_current.custom_default_salary
                        grade_found = True
                        break
                except Exception as e:
                    frappe.log_error(f"Grade fetch failed for '{row.new}': {e}", "Employee Promotion")

        # If no Grade was found in promotion_details, and current revised_ctc might be from Grade, clear it
        if not grade_found:
            self.revised_ctc = 0.0
