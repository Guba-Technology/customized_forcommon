import frappe
from frappe import _

from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import (
    StockReconciliation
)


class CustomStockReconciliation(StockReconciliation):

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


    def get_gl_entries(self, warehouse_account=None):

        if not self.cost_center:
            frappe.throw(
                _("Please enter Cost Center")
            )


        enabled = frappe.db.get_value(
            "Company",
            self.company,
            "custom_enable_item_group_based_inventory"
        )


        # Default ERPNext behavior
        if not enabled:
            return super().get_gl_entries(
                warehouse_account
            )


        if not warehouse_account:
            return super().get_gl_entries(
                warehouse_account
            )


        # Replace warehouse inventory accounts with Item Group inventory accounts
        for item in self.items:

            if not item.warehouse:
                continue


            item_group_account = self.get_item_group_inventory_account(
                item.item_code
            )


            if item.warehouse in warehouse_account:

                warehouse_account[item.warehouse]["account"] = (
                    item_group_account
                )


        """
        Let ERPNext create the GL entries
        This preserves:
        - Opening Stock logic
        - Stock Adjustment account
        - Cost Center
        - Difference calculation
        """
        return super().get_gl_entries(
            warehouse_account
        )