import frappe
from frappe.model.document import Document
from frappe.utils import flt


class InterCompanyAssetTransfer(Document):
    def on_submit(self):
        self.make_gl_entries()

    def make_gl_entries(self):
        for item in self.assets:
            if not item.source_company or not item.target_company:
                frappe.throw(f"Both From Company and To Company are required for asset {item.asset}")

            # Get asset details
            asset_doc = frappe.get_doc("Asset", item.asset)
            asset_category = asset_doc.asset_category

            if not asset_category:
                frappe.throw(f"Asset {item.asset} has no Asset Category linked.")

            # Use the correct value field
            asset_value = (
                asset_doc.gross_purchase_amount or
                asset_doc.value_after_depreciation or
                asset_doc.opening_accumulated_depreciation or
                0
            )

            frappe.msgprint(f"""
                Asset: {item.asset}
                Gross Purchase Amount: {asset_doc.gross_purchase_amount}
                Value After Depreciation: {asset_doc.value_after_depreciation}
                Opening Accumulated Depreciation: {asset_doc.opening_accumulated_depreciation}
                Final Asset Value: {asset_value}
            """)

            if asset_value == 0:
                frappe.throw(f"Asset {item.asset} has zero value. Cannot create GL entries.")

            # Fetch fixed asset accounts per company from child table
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

            if not from_account:
                frappe.throw(f"Missing Fixed Asset Account for source company {item.source_company} under category {asset_category}")
            if not to_account:
                frappe.throw(f"Missing Fixed Asset Account for target company {item.target_company} under category {asset_category}")

            # Ensure account exists
            if not frappe.db.exists("Account", from_account):
                frappe.throw(f"Account {from_account} does not exist")
            if not frappe.db.exists("Account", to_account):
                frappe.throw(f"Account {to_account} does not exist")

            # Create GL entries with proper rounding
            asset_value = flt(asset_value, 2)

            gl_entries = [
                {
                    "posting_date": self.transaction_date,
                    "transaction_date": self.transaction_date,
                    "company": item.source_company,
                    "account": from_account,
                    "credit": asset_value,
                    "debit": 0,
                    "credit_in_account_currency": asset_value,
                    "debit_in_account_currency": 0,
                    "against": to_account,
                    "against_voucher_type": "Inter Company Asset Transfer",
                    "against_voucher": self.name,
                    "remarks": f"Asset transfer from {item.source_company} to {item.target_company} for {item.asset}",
                    "voucher_type": "Inter Company Asset Transfer",
                    "voucher_no": self.name,
                    "is_cancelled": 0,
                    "is_opening": "No"
                },
                {
                    "posting_date": self.transaction_date,
                    "transaction_date": self.transaction_date,
                    "company": item.target_company,
                    "account": to_account,
                    "debit": asset_value,
                    "credit": 0,
                    "debit_in_account_currency": asset_value,
                    "credit_in_account_currency": 0,
                    "against": from_account,
                    "against_voucher_type": "Inter Company Asset Transfer",
                    "against_voucher": self.name,
                    "remarks": f"Asset received from {item.source_company} to {item.target_company} for {item.asset}",
                    "voucher_type": "Inter Company Asset Transfer",
                    "voucher_no": self.name,
                    "is_cancelled": 0,
                    "is_opening": "No"
                },
            ]

            # Insert GL entries
            for entry in gl_entries:
                try:
                    gl = frappe.new_doc("GL Entry")
                    gl.update(entry)
                    gl.insert(ignore_permissions=True, ignore_mandatory=True)
                    frappe.db.commit()  # Ensure the entry is committed to database
                    frappe.msgprint(f"Created GL Entry: {gl.name} - Account: {gl.account}, Debit: {gl.debit}, Credit: {gl.credit}")
                except Exception as e:
                    frappe.throw(f"Failed to create GL Entry: {str(e)}")

            frappe.msgprint(f"Successfully created GL entries for asset {item.asset} with value {asset_value}")
            # Update Asset's company after GL transfer
            asset_doc.db_set("company", item.target_company)
            frappe.msgprint(f"Asset {item.asset} is now owned by company {item.target_company}")
    def on_cancel(self):
        self.cancel_gl_entries()

    def cancel_gl_entries(self):
        # Cancel related GL entries
        gl_entries = frappe.get_all("GL Entry",
            filters={"voucher_type": "Inter Company Asset Transfer", "voucher_no": self.name, "is_cancelled": 0})

        for gl in gl_entries:
            try:
                gl_doc = frappe.get_doc("GL Entry", gl.name)
                gl_doc.cancel()
                frappe.db.commit()
            except Exception as e:
                frappe.throw(f"Failed to cancel GL Entry {gl.name}: {str(e)}")