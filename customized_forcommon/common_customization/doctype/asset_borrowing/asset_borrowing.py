import frappe
from frappe.model.document import Document

class AssetBorrowing(Document):

    def on_submit(self):

        asset = frappe.get_doc("Asset", self.asset)

        # Update Asset Status to Borrowed
        frappe.db.set_value("Asset", self.asset, "status", "Borrowed")
        self.original_company = asset.company
        # 1. Update Asset Company
        if self.asset and self.borrower:
            frappe.db.set_value("Asset", self.asset, "company", self.borrower)

        # 2. Set Status to Borrowed
        self.status = "Borrowed"
        frappe.db.set_value("Asset Borrowing", self.name, "status", "Borrowed")

        frappe.msgprint(f"Asset {self.asset} successfully borrowed by {self.borrower}.")

    def on_cancel(self):
        # Reset status to Active (or Available)
        frappe.db.set_value("Asset", self.asset, "status", "Submitted")
        if self.original_company:
            frappe.db.set_value("Asset", self.asset, "company", self.original_company)
        frappe.db.set_value("Asset Borrowing", self.name, "status", "Cancelled")
@frappe.whitelist()
def return_asset(asset_name):
    # Validate asset exists
    asset = frappe.get_doc("Asset", asset_name)

    if asset.status != "Borrowed":
        frappe.throw("Only borrowed assets can be returned.")

    borrowing = frappe.get_value(
        "Asset Borrowing",
        {"asset": asset_name, "status": "Borrowed"},
        ["name", "original_company"],
        as_dict=True
    )

    # Reset the asset status
    frappe.db.set_value("Asset", asset_name, "status", "Submitted")
    frappe.db.set_value("Asset", asset_name, "company", borrowing.original_company)
    frappe.db.set_value("Asset Borrowing", borrowing.name, "status", "Returned")
    frappe.msgprint(f"Asset {asset_name} successfully returned.")

    return True
