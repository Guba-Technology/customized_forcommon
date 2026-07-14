import frappe
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import PurchaseReceipt

class CustomPurchaseReceipt(PurchaseReceipt):
    def get_item_group_inventory_account(self, item_code):

        item_group = frappe.db.get_value(
            "Item",
            item_code,
            "item_group"
        )

        account = frappe.db.get_value(
            "Item Default",
            {
                "parent": item_group,
                "company": self.company
            },
            "custom_default_inventory_account"
        )

        if not account:
            frappe.throw(
                f"""
                Missing Item Group Inventory Account

                Item: {item_code}
                Item Group: {item_group}
                """
            )

        return account


    def get_gl_entries(
        self,
        warehouse_account=None,
        via_landed_cost_voucher=False
    ):

        enabled = frappe.db.get_value(
            "Company",
            self.company,
            "custom_enable_item_group_based_inventory"
        )

        if not enabled:
            return super().get_gl_entries(
                warehouse_account,
                via_landed_cost_voucher
            )

        if warehouse_account:
            for item in self.items:
                if item.warehouse:
                    item_group_account = self.get_item_group_inventory_account(
                        item.item_code
                    )
                    if item.warehouse in warehouse_account:

                        warehouse_account[item.warehouse]["account"] = (
                            item_group_account
                        )

        return super().get_gl_entries(
            warehouse_account,
            via_landed_cost_voucher
        )