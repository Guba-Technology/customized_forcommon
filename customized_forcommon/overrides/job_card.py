from erpnext.manufacturing.doctype.job_card.job_card import JobCard
import frappe
from frappe import _

class CustomJobCard(JobCard):
    def on_submit(self):
        super().on_submit()
        self.check_if_quality_inspection_required()
    def check_if_quality_inspection_required(self):
        if self.custom_inspection_required_before_submit:
            quality_inspection = frappe.db.get_value("Quality Inspection", {"reference_name": self.name, "docstatus": 1,"inspection_type": "In Process", "reference_type": "Job Card", "status": "Accepted"}, "name")
            if not quality_inspection:
                frappe.throw(_("Submission blocked. A valid, 'Accepted' Quality Inspection must be linked and submitted for this Job Card."))

    
