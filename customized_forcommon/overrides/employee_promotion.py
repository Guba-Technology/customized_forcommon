import frappe
from frappe import _
from hrms.hr.doctype.employee_promotion.employee_promotion import EmployeePromotion

class CustomEmployeePromotion(EmployeePromotion):
    def validate(self):
        super().validate()
        self.set_revised_ctc_from_grade()
        self.set_revised_ctc_from_step()

    def set_revised_ctc_from_grade(self):
        for row in self.promotion_details:
            if row.property == "Grade":
                grade_current = grade_new = None
                # Fetch current and new grades
                if row.current:
                    grade_current = frappe.get_doc("Employee Grade", row.current)
                else:
                    continue

                if row.new:
                    grade_new = frappe.get_doc("Employee Grade", row.new)
                    
                    if grade_new.custom_default_salary > grade_current.custom_default_salary:
                        # If the new grade's salary is greater, set it as revised_ctc
                        self.revised_ctc = grade_new.custom_default_salary
                        # remove step from employee if set
                        frappe.db.set_value("Employee", self.employee, "custom_step", None)
                    else:
                        # If the new grade's salary is not greater, fallback to current grade's salary
                        self.revised_ctc = grade_current.custom_default_salary
                        # remove step from employee if set
                        frappe.db.set_value("Employee", self.employee, "custom_step", None)
                else:
                    # No new grade, fallback to current
                    self.revised_ctc = grade_current.custom_default_salary
                    # remove step from employee if set
                    frappe.db.set_value("Employee", self.employee, "custom_step", None)


    # This method sets the revised CTC based on the Step details
    def set_revised_ctc_from_step(self):
        grade_row = step_row = None

        # First, find the Grade and Step rows (if any)
        for row in self.promotion_details:
            if row.property == "Grade":
                grade_row = row
            if row.property == "Step":
                step_row = row

        # Prefer Step over Grade if both exist
        if grade_row and step_row:
            # Get new Grade and new Step
            grade = frappe.get_doc("Employee Grade", grade_row.new)
            step = frappe.get_doc("Employee Step", step_row.new)

            if step.salary < grade.custom_default_salary:
                frappe.throw(_("New Step salary cannot be less than the New Grade salary"))

        # Now handle Step logic
        if step_row:
            step_current = step_new = None

            if step_row.current:
                step_current = frappe.get_doc("Employee Step", step_row.current)

            if step_row.new:
                step_new = frappe.get_doc("Employee Step", step_row.new)
            else:
                frappe.throw(_("New Step is required for promotion."))

            # Validate and assign revised CTC
            if step_current and step_new:
                if step_new.salary < step_current.salary:
                    frappe.throw(_("New Step salary cannot be less than the Current Step salary"))
                else:
                    self.revised_ctc = step_new.salary

            elif not step_current and step_new:
                # If no current step, check the last promotion's revised CTC
                latest_promotion_list = frappe.get_all(
                    "Employee Promotion",
                    filters={"employee": self.employee, "docstatus": 1},
                    fields=["name"],
                    order_by="creation desc",
                )

                promotion = None
                if latest_promotion_list:
                    promotion = frappe.get_doc("Employee Promotion", latest_promotion_list[0].name)

                # If we have a promotion, check its revised CTC
                if promotion and step_new.salary < promotion.revised_ctc:
                    frappe.throw(_(f"New Step salary cannot be less than the Revised CTC of the last promotion of {self.employee}."))
                else:
                    self.revised_ctc = step_new.salary

            # Update employee step
            frappe.db.set_value("Employee", self.employee, "custom_step", step_new.name)
            frappe.msgprint(_(f"New Step salary {self.revised_ctc} set as Revised CTC"), alert=True)
