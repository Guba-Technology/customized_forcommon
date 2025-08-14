# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class BulkEmployeePromotion(Document):
    def validate(self):
        self.validate_step_salary()
        self.make_docstatus_to_one()
    
    def make_docstatus_to_one(self):
        """Ensure the document is set to submitted state."""
        if self.status == "Approved":
            self.docstatus = 1
    def validate_step_salary(self):
        current_step_salary = frappe.db.get_value(
           "Employee Step",
           {"step": self.current_step},
             "salary"
            )
        new_step_salary = frappe.db.get_value(
            "Employee Step",
            {"step": self.new_step},
            "salary"
        )
        if self.current_step and self.new_step:
            if current_step_salary >= new_step_salary:
                frappe.throw(_("New step salary must be greater than the current step salary."))

    def on_submit(self):
        if self.status !=  "Approved":
            frappe.throw("You can't submit with no Approved status")

    # def on_trash(self):
    #     if self.status == "Approved" and self.docstatus == 1:
    #         frappe.throw(_("Cannot delete a submitted Bulk Employee Promotion document."))
            
    # def before_cancel(self):
    #     if self.status == "Approved":
    #         frappe.throw(_("Cannot cancel a submitted Bulk Employee Promotion document."))
        
        
@frappe.whitelist()
def get_employees_by_grade_or_step(grade=None, step=None):
    filters = {"status": "Active"}

    if grade:
        filters["grade"] = grade
    if step:
        filters["custom_step"] = step

    if not filters.get("grade") and not filters.get("custom_step"):
        return []

    employees = frappe.get_all("Employee", filters, ["name", "employee_name", "department", "designation", "grade", "custom_step"])
    
    return employees


@frappe.whitelist()
def promote_by_grade(docname):
    doc = frappe.get_doc("Bulk Employee Promotion", docname)

    if not doc.employees:
        frappe.throw(_("No employees to promote."))

    # Suppress CTC messages from employee validate
    frappe.flags.suppress_ctc_message = True

    for row in doc.employees:
        emp_promotion = frappe.new_doc("Employee Promotion")
        emp_promotion.employee = row.employee
        emp_promotion.promotion_date = doc.promotion_date
        emp_promotion.custom_promotion_reason = "Bulk"

        emp_promotion.append("promotion_details", {
            "property": "Grade",
            "current": row.grade,
            "new": doc.new_grade
        })

        # Update employee grade and suppress messages
        frappe.db.set_value("Employee", row.employee, "grade", doc.new_grade)

        emp_promotion.insert()
        emp_promotion.submit()

    return _("Promotions created successfully for {0} employees.").format(len(doc.employees))


@frappe.whitelist()
def promote_by_step(docname):
    doc = frappe.get_doc("Bulk Employee Promotion", docname)
    
    if not doc.employees:
        frappe.throw(_("No employees to promote."))

    # Suppress CTC messages from employee validate
    frappe.flags.suppress_ctc_message = True
    frappe.flags.suppress_revised_ctc_message = True

    for row in doc.employees:
        emp_promotion = frappe.new_doc("Employee Promotion")
        emp_promotion.employee = row.employee
        emp_promotion.promotion_date = doc.promotion_date
        emp_promotion.custom_promotion_reason = "Bulk"

        emp_promotion.append("promotion_details", {
            "property": "Step",
            "current": row.step,
            "new": doc.new_step
        })

        # Update employee step and suppress messages
        frappe.db.set_value("Employee", row.employee, "custom_step", doc.new_step)

        emp_promotion.insert()
        emp_promotion.submit()

    return _("Promotions created successfully for {0} employees.").format(len(doc.employees))