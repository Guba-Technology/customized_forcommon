import frappe
from frappe.model.document import Document

class AssetBorrowing(Document):

    def on_submit(self):
        # Update Asset Status to Borrowed
        frappe.db.set_value("Asset", self.asset, "status", "Borrowed")

    def on_cancel(self):
        # Reset status to Active (or Available)
        frappe.db.set_value("Asset", self.asset, "status", "Active")
