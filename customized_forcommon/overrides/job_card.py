from erpnext.manufacturing.doctype.job_card.job_card import JobCard
import frappe
from frappe import _

class CustomJobCard(JobCard):
    def on_submit(self):
        super().on_submit()
        self.set_accepted_rejected_rework_qty_in_work_order()

    def set_accepted_rejected_rework_qty_in_work_order(self):
        work_order = frappe.get_doc("Work Order", self.work_order)

        if work_order.operations:
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
