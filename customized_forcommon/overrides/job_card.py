from erpnext.manufacturing.doctype.job_card.job_card import JobCard
import frappe
from frappe import _

class CustomJobCard(JobCard):
    def on_submit(self):
        super().on_submit()
        self.set_accepted_rejected_rework_qty_in_work_order()
        self.check_total_qty_of_job_card_is_not_less_than_accepted_rejected_rework_qty()

    def set_accepted_rejected_rework_qty_in_work_order(self):
        work_order = frappe.get_doc("Work Order", self.work_order)

        if work_order.operations and work_order.status == "In Process":
            last_operation_row = work_order.operations[-1]

            if self.operation == last_operation_row.operation:
                # Use db.set_value to update submitted Work Order
                frappe.db.set_value("Work Order", self.work_order, {
                    "custom_accepted_quantity": self.custom_accepted_quantity,
                    "custom_rejected_quantity": self.custom_rejected_quantity,
                    "custom_rework_quantity": self.custom_rework_quantity
                })

                link = f'<a href="/app/work-order/{work_order.name}">{work_order.name}</a>'
                frappe.msgprint(_("Submitted Work Order updated with accepted, rejected, and rework quantities. {0}").format(link))

        # Insert directly to DB without calling save on parent
        frappe.get_doc({
            "doctype": "Job Card Status Tracking",  # the child table name in the Work Order
            "parent": self.work_order,
            "parenttype": "Work Order",
            "parentfield": "custom_job_card_status",
            "linked_operation": self.operation,
            "linked_job_card": self.name,
            "total_completed_quantity": self.total_completed_qty,
            "accepted_quantity": self.custom_accepted_quantity,
            "rejected_quantity": self.custom_rejected_quantity,
            "rework_quantity": self.custom_rework_quantity
        }).insert(ignore_permissions=True)
    
    def check_total_qty_of_job_card_is_not_less_than_accepted_rejected_rework_qty(self):
        if self.custom_accepted_quantity and self.custom_rejected_quantity and self.custom_rework_quantity:
                total_qty = (
                    float(self.custom_accepted_quantity)
                    + float(self.custom_rejected_quantity)
                    + float(self.custom_rework_quantity)
                )
                if total_qty > self.total_completed_qty:
                    frappe.throw(
                        "Total of Accepted, Rejected, and Rework quantities cannot exceed the Job Card's total completed Qty."
                    )
