from erpnext.stock.doctype.quality_inspection.quality_inspection import QualityInspection

import frappe

class CustomQualityInspection(QualityInspection):
    def validate(self):
        super().validate()
        self.set_status_of_readings_table()
        self.check_total_qty_of_job_card_is_not_less_than_accepted_rejected_rework_qty()
     
    def set_status_of_readings_table(self):
        if self.readings:
            for row in self.readings:
                if (
                    row.custom_no_of_accepted_quantity is not None
                    and row.custom_no_of_rejected_quantity is not None
                    and row.custom_no_of_rework is not None
                ):
                    row.status = ""

    def check_total_qty_of_job_card_is_not_less_than_accepted_rejected_rework_qty(self):
        if self.reference_type == "Job Card" and self.reference_name:
            completed_qty = frappe.db.get_value(
            "Job Card",
            self.reference_name,
            "total_completed_qty"
            )
            if self.custom_no_of_accepted_quantity and self.custom_no_of_rejected_quantity and self.custom_no_of_rework:
                total_qty = (
                    float(self.custom_no_of_accepted_quantity)
                    + float(self.custom_no_of_rejected_quantity)
                    + float(self.custom_no_of_rework)
                )
                if total_qty > completed_qty:
                    frappe.throw(
                        "Total of Accepted, Rejected, and Rework quantities cannot exceed the Job Card's total completed Qty."
                    )
    def on_submit(self):
        super().on_submit()
        self.set_accepted_rejected_rework_qty_in_job_card()

    def set_accepted_rejected_rework_qty_in_job_card(self):
        if self.reference_type == "Job Card" and self.reference_name:
            job_card = frappe.get_doc("Job Card", self.reference_name)
            if job_card.docstatus != 1:
                job_card.custom_accepted_quantity = self.custom_no_of_accepted_quantity
                job_card.custom_rejected_quantity = self.custom_no_of_rejected_quantity
                job_card.custom_rework_quantity = self.custom_no_of_rework
                job_card.save()
