from hrms.hr.doctype.leave_encashment.leave_encashment import LeaveEncashment
import frappe

class CustomLeaveEncashment(LeaveEncashment):
    def before_save(self):
        # super().before_save()
        self.calculate_total_encashment_amount()
    def before_submit(self):
        self.calculate_total_encashment_amount()
        super().before_submit()
    def on_submit(self):
        super().on_submit()
        self.calculate_total_encashment_amount()
    def calculate_total_encashment_amount(self):
        employee = frappe.get_doc("Employee", self.employee)
        ctc = employee.ctc
        if not ctc:
            frappe.throw("Cost to Company (CTC) is not set for the employee.")
        eca = ctc * self.encashment_days / 30
        self.encashment_amount = eca