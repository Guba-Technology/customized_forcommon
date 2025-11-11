import frappe
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.accounts.general_ledger import make_gl_entries


class InterCompanyAssetTransfer(Document):
    def on_submit(self):
        """On submission:
        1️⃣ Create GL Entries (transfer value)
        2️⃣ Create temporary Asset Receipts in target companies
        """
        frappe.db.set_value(self.doctype, self.name, "status", "In Transit")
        self.make_gl_entries()
        self.create_asset_receipts_in_target_company()
    def before_cancel(self):
        # Optionally check if GL Entries exist, then allow cancellation
        gl_exists = frappe.db.exists({
            "doctype": "GL Entry",
            "voucher_type": "Inter Company Asset Transfer",
            "voucher_no": self.name,
            "docstatus": 1
        })
        if not gl_exists:
            frappe.throw("No GL Entries found to cancel.")
    def make_gl_entries(self):
        """Handle debit/credit between source and target companies"""
        all_gl_entries = []

        for item in self.assets:
            self.validate_asset_item(item)
            asset_value = self.get_asset_transfer_value(item.asset)

            gl_entries = self.prepare_gl_entries_for_asset(item, asset_value)
            all_gl_entries.extend(gl_entries)


        # Create GL Entry documents instead of dictionaries
        self.create_gl_entry_documents(all_gl_entries)

    def create_gl_entry_documents(self, gl_entries_list):
        """Create GL Entry documents from the list of dictionaries"""
        for gl_dict in gl_entries_list:
            gl_entry = frappe.get_doc({
                "doctype": "GL Entry",
                **gl_dict
            })
            gl_entry.insert(ignore_permissions=True)
            gl_entry.submit()

    def validate_asset_item(self, item):
        """Validate required fields for asset item"""
        if not item.source_company or not item.target_company:
            frappe.throw(f"Both Source and Target Company are required for asset {item.asset}")
    def get_asset_transfer_value(self, asset_name):
        """Get the appropriate transfer value for the asset"""
        asset_doc = frappe.get_doc("Asset", asset_name)
        if not asset_doc.asset_category:
            frappe.throw(f"Asset {asset_name} has no Asset Category linked.")
        # Determine value for transfer - check fields in priority order
        asset_value = 0
        field_priority = ['value_after_depreciation', 'gross_purchase_amount', 'opening_accumulated_depreciation']

        for field in field_priority:
            field_value = flt(getattr(asset_doc, field, 0), 2)

            if field_value > 0:
                asset_value = field_value
                break
            else:
                frappe.msgprint(f" Field '{field}' has zero or negative value: {field_value}")


        if asset_value == 0:
            frappe.throw(f"Asset {asset_name} has zero value. Cannot create GL entries.")

        return asset_value

    def prepare_gl_entries_for_asset(self, item, asset_value):
        """Prepare GL entries for a single asset transfer, including intercompany receivable/payable"""

        asset_doc = frappe.get_doc("Asset", item.asset)
        asset_category = asset_doc.asset_category

        # Asset accounts
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

        # Intercompany accounts
        intercompany_receivable = "InterCompany Recievable Debit - G"
        intercompany_payable = "InterCompany Payable Credit - T"

        from_currency = frappe.db.get_value("Account", from_account, "account_currency")
        to_currency = frappe.db.get_value("Account", to_account, "account_currency")
        from_cost_center = frappe.db.get_value("Company", item.source_company, "cost_center")
        to_cost_center = frappe.db.get_value("Company", item.target_company, "cost_center")

        gl_entries = [
            # 1️⃣ Original asset transfer entries
            {
                "posting_date": self.transaction_date,
                "company": item.source_company,
                "account": from_account,
                "credit": asset_value,
                "debit": 0,
                "against": to_account,
                "voucher_type": "Inter Company Asset Transfer",
                "voucher_no": self.name,
                "remarks": f"Asset transfer out: {item.asset}",
                "account_currency": from_currency,
                "credit_in_account_currency": asset_value,
                "cost_center": from_cost_center,
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
                "remarks": f"Asset transfer in: {item.asset}",
                "account_currency": to_currency,
                "debit_in_account_currency": asset_value,
                "cost_center": to_cost_center,
            },
            # 2️⃣ Intercompany accounts
            {
                "posting_date": self.transaction_date,
                "company": item.source_company,
                "account": intercompany_receivable,
                "debit": asset_value,
                "credit": 0,
                "against": intercompany_payable,
                "voucher_type": "Inter Company Asset Transfer",
                "voucher_no": self.name,
                "remarks": f"Intercompany Receivable for asset: {item.asset}",
                "account_currency": from_currency,
                "debit_in_account_currency": asset_value,
                "cost_center": from_cost_center,
            },
            {
                "posting_date": self.transaction_date,
                "company": item.target_company,
                "account": intercompany_payable,
                "debit": 0,
                "credit": asset_value,
                "against": intercompany_receivable,
                "voucher_type": "Inter Company Asset Transfer",
                "voucher_no": self.name,
                "remarks": f"Intercompany Payable for asset: {item.asset}",
                "account_currency": to_currency,
                "credit_in_account_currency": asset_value,
                "cost_center": to_cost_center,
            },
        ]

        return gl_entries


    def create_asset_receipts_in_target_company(self):
        """Create Asset Receipt docs in target company"""
        for item in self.assets:
            receipt = frappe.get_doc({
                "doctype": "Asset Receipt",
                "source_company": item.source_company,
                "target_company": item.target_company,
                "transfer_reference": self.name,
                "location": None,
                "status": "In Transit",
            })

            receipt.append("asset_list", {
                "asset": item.asset,
                "asset_name": item.asset_name,
                "source_company": item.source_company,
                "target_company": item.target_company,
            })

            receipt.insert(ignore_permissions=True)

