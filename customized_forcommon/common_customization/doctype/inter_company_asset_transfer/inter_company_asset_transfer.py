import frappe
from frappe.model.document import Document
from frappe.utils import flt


class InterCompanyAssetTransfer(Document):
    def on_submit(self):
        """On submission:
        1️⃣ Create GL Entries (transfer value)
        2️⃣ Create temporary Asset Receipts in target companies
        """
        self.make_gl_entries()
        frappe.db.commit()
        self.create_asset_receipts_in_target_company()

    # ------------------------------------------------------------
    # 1️⃣ GL Transfer Logic
    # ------------------------------------------------------------
    def make_gl_entries(self):
        """Handle debit/credit between source and target companies"""
        for item in self.assets:
            if not item.source_company or not item.target_company:
                frappe.throw(f"Both Source and Target Company are required for asset {item.asset}")

            # Fetch asset details
            asset_doc = frappe.get_doc("Asset", item.asset)
            asset_category = asset_doc.asset_category
            if not asset_category:
                frappe.throw(f"Asset {item.asset} has no Asset Category linked.")

            # frappe.msgprint(f"""
            # <b>Debug Info</b><br>
            # Asset: {item.asset}<br>
            # Gross Purchase Amount: {asset_doc.gross_purchase_amount}<br>
            # Value After Depreciation: {asset_doc.value_after_depreciation}<br>
            # Opening Accumulated Depreciation: {asset_doc.opening_accumulated_depreciation}
            # """)

            # Determine value for transfer
            asset_value = flt(
                asset_doc.gross_purchase_amount
                or asset_doc.value_after_depreciation
                or asset_doc.opening_accumulated_depreciation
                or 0,
                2
            )

            if asset_value == 0:
                frappe.throw(f"Asset {item.asset} has zero value. Cannot create GL entries.")

            # Get accounts from Asset Category Account
            from_account = frappe.db.get_value(
                "Asset Category Account",
                {"parent": asset_category, "company_name": item.source_company},
                "fixed_asset_account"
            )
            to_account = frappe.db.get_value(
                "Asset Category Account",
                {"parent": asset_category, "company_name": item.target_company},
                "fixed_asset_account"
            )

            if not from_account or not to_account:
                frappe.throw(f"Missing Fixed Asset Account setup for asset category {asset_category}")

            # Create two GL entries (credit + debit)
            gl_entries = [
                {
                    "posting_date": self.transaction_date,
                    "company": item.source_company,
                    "account": from_account,
                    "credit": asset_value,
                    "debit": 0,
                    "against": to_account,
                    "voucher_type": "Inter Company Asset Transfer",
                    "voucher_no": self.name,
                    "remarks": f"Asset transfer out: {item.asset}"
                },
                {
                    "posting_date": self.transaction_date,
                    "company": item.target_company,
                    "account": to_account,
                    "debit": asset_value,
                    "credit": 0,
                    "against": from_account,
                    "voucher_type": "Inter Company Asset Transfer",
                    "voucher_no": self.name,
                    "remarks": f"Asset transfer in: {item.asset}"
                }
            ]

            # Save GL entries
            for entry in gl_entries:
                gl = frappe.new_doc("GL Entry")
                gl.update(entry)
                gl.insert(ignore_permissions=True, ignore_mandatory=True)
                frappe.db.commit()
        frappe.msgprint("✅ Successfully created GL entries for all transferred assets.")

    # ------------------------------------------------------------
    # 2️⃣ Create Asset Receipt in Target Company
    # ------------------------------------------------------------
    def create_asset_receipts_in_target_company(self):
        """Create Asset Receipt docs in target company"""
        for item in self.assets:
            # Create new Asset Receipt
            receipt = frappe.get_doc({
                "doctype": "Asset Receipt",
                "source_company": item.source_company,
                "target_company": item.target_company,
                "transfer_reference": self.name,
                "location": None,  # user sets later
                "status": "Pending Location",
            })

            # Add transferred asset to the child table
            receipt.append("asset_list", {
                "asset": item.asset,
                "asset_name": item.asset_name,
                "source_company": item.source_company,
                "target_company": item.target_company,
            })

            # Save new receipt
            receipt.insert(ignore_permissions=True)
            frappe.msgprint(f"📦 Created Asset Receipt <b>{receipt.name}</b> in {item.target_company}")

    # ------------------------------------------------------------
    # 3️⃣ Cancel Logic
    # ------------------------------------------------------------
    def on_cancel(self):
        """Cancel related GL entries if this transfer is cancelled"""
        gl_entries = frappe.get_all(
            "GL Entry",
            filters={
                "voucher_type": "Inter Company Asset Transfer",
                "voucher_no": self.name,
                "is_cancelled": 0
            },
            pluck="name"
        )

        for gl_name in gl_entries:
            gl_doc = frappe.get_doc("GL Entry", gl_name)
            gl_doc.cancel()

        frappe.msgprint("🗑️ Cancelled all GL Entries related to this transfer.")
