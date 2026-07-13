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
            frappe.msgprint(
                _("Please enter Cost Center"),
                raise_exception=1
            )


        enabled = frappe.db.get_value(
            "Company",
            self.company,
            "custom_enable_item_group_based_inventory"
        )


        if not enabled:
            return super().get_gl_entries(
                warehouse_account
            )


        if not warehouse_account:

            from erpnext.stock.doctype.stock_entry.stock_entry import (
                get_warehouse_account_map
            )

            warehouse_account = get_warehouse_account_map(
                self.company
            )


        # Replace warehouse account by Item Group account
        for item in self.items:

            if item.warehouse:

                item_group_account = (
                    self.get_item_group_inventory_account(
                        item.item_code
                    )
                )

                if item.warehouse in warehouse_account:

                    warehouse_account[item.warehouse]["account"] = (
                        item_group_account
                    )


        return super().get_gl_entries(
            warehouse_account
        )