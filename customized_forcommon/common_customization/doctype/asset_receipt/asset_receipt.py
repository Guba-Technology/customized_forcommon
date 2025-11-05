import frappe
from frappe.model.document import Document

class AssetReceipt(Document):
    def validate(self):
        """Update status automatically when location is filled"""
        if self.location and self.status == "Pending Location":
            self.status = "Ready to Create Asset"


@frappe.whitelist()
def create_asset_from_receipt(receipt_name):
    """Update transferred Asset's company to target company"""
    receipt = frappe.get_doc("Asset Receipt", receipt_name)

    # Basic validation
    if not receipt.asset_list:
        frappe.throw("No assets found in this receipt.")
    if not receipt.location:
        frappe.throw("Location is missing. Please select location before processing.")

    for item in receipt.asset_list:
        if not item.asset:
            frappe.throw("Asset is missing in one of the rows.")
        if not item.target_company:
            frappe.throw(f"Target Company is missing for asset {item.asset}")

        # Get the asset
        asset_doc = frappe.get_doc("Asset", item.asset)

        # Optional: check if already belongs to target company
        if asset_doc.company == item.target_company:
            frappe.msgprint(f"Asset {asset_doc.name} already belongs to {item.target_company}. Skipping.")
            continue

        # Update company and location
        asset_doc.db_set("company", item.target_company)
        asset_doc.db_set("location", receipt.location)

        frappe.msgprint(f"✅ Updated Asset <b>{asset_doc.name}</b> to company {item.target_company}")

    # Mark receipt as complete
    receipt.status = "Asset Created"
    receipt.save()
