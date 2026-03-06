import frappe
from erpnext.setup.doctype.employee.employee import Employee
from frappe.utils import add_years, getdate, nowdate

class CustomEmployee(Employee):
    def validate(self):
        super().validate()
        # frappe.msgprint("CustomEmployee.validate triggered for CTC setting")
        # self.set_ctc_from_grade_and_promotion()
        self.validate_18_years_old()

    def set_ctc_from_grade_and_promotion(self):
        """Set CTC from Employee Grade and Promotion if available."""
        # If suppression flag is set, skip showing messages
        suppress_msg = frappe.flags.suppress_ctc_message if hasattr(frappe.flags, "suppress_ctc_message") else False

        promotion_salary = None

        promotion_list = frappe.get_list(
            "Employee Promotion",
            filters={"employee": self.name, "docstatus": 1},
            fields=["name"],
            order_by="creation desc",
            limit_page_length=1
        )

        promotion = None
        if promotion_list:
            promotion = frappe.get_doc("Employee Promotion", promotion_list[0].name)
            promotion_salary = promotion.revised_ctc

        grade = None
        default_salary = None
        if self.grade:
            grade = frappe.get_doc("Employee Grade", self.grade)
            default_salary = grade.custom_default_salary

        step = None
        step_salary = None
        if self.custom_step:
            step = frappe.get_doc("Employee Step", self.custom_step)
            step_salary = step.salary

        # CTC assignment logic
        if promotion:
            self.ctc = promotion_salary
            if not suppress_msg:
                frappe.msgprint(f"CTC set to {promotion_salary} from latest promotion: {promotion.name}.", alert=True)
        elif step and grade:
            if step_salary < default_salary:
                self.ctc = default_salary
                if not suppress_msg:
                    frappe.msgprint(f"CTC set to {default_salary} from grade: {self.grade}.", alert=True)
            else:
                self.ctc = step_salary
                if not suppress_msg:
                    frappe.msgprint(f"CTC set to {step_salary} from step: {self.custom_step}.", alert=True)

        elif not grade and step:
            self.ctc = step_salary
            if not suppress_msg:
                    frappe.msgprint(f"CTC set to {step_salary} from step: {self.custom_step}.", alert=True)
        elif not step and grade:
            self.ctc = default_salary
            if not suppress_msg:
                    frappe.msgprint(f"CTC set to {default_salary} from grade: {self.grade}.", alert=True)
        else:
            self.ctc = 0
            if not suppress_msg:
                frappe.msgprint("No Employee Grade or Step or Promotion found to set CTC.", alert=True)


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