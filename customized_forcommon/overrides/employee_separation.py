import frappe
from hrms.hr.doctype.employee_separation.employee_separation import EmployeeSeparation
from frappe import _

class CustomEmployeeSeparation(EmployeeSeparation):
    def validate(self):
        super().validate()
        self.restrict_separation_for_employees_with_active_warranty_requests()
        
    def restrict_separation_for_employees_with_active_warranty_requests(self):
        """Restrict separation if there are active warranty requests for the employee."""
        approved_warranty_request = frappe.get_all(
            "Warranty Request",
            filters={
                "employee": self.employee,
                "status": "Active",  # Only consider active warranty requests
                "name": ["!=", self.name]  # Exclude current separation request
            },
            fields=["name"]
        )
        if approved_warranty_request:
            # Generate clickable links
            links = ", ".join([
                f'<a href="/app/warranty-request/{req.name}">{req.name}</a>'
                for req in approved_warranty_request
            ])
            frappe.throw(
                _("Employee cannot be separated as there is active warranty request: {0}").format(links),
                title="Active Warranty Requests"
            )
    def on_submit(self):
        # if `boarding_status` is the relevant field, set it to "Completed".
        self.db_set("boarding_status", "Completed") # Assuming 'Completed' is a valid status for separation
        self.reload()

