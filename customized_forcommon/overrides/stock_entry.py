import frappe
from frappe import _
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry as ERPNextStockEntry
from frappe.utils import flt
from erpnext.accounts.general_ledger import process_gl_map

class CustomStockEntry(ERPNextStockEntry):

    # def on_update(self):
    #     """Handle Draft → In Transit (docstatus = 0)"""
    #     if self.stock_entry_type != "Material Transfer":
    #         super().on_update()  # only call default logic for other types
    #         return

    #     if self.docstatus == 0 and self.custom_transfer_status == "In Transit":
    #         self.send_to_transit()

    # def on_submit(self):
    #     """Handle In Transit → Completed (docstatus = 1)"""
    #     if self.stock_entry_type != "Material Transfer":
    #         super().on_submit()  # only call default logic for other types
    #         return

    #     if self.custom_transfer_status == "Completed":
    #         self.complete_transfer()

    # def send_to_transit(self):
    #     """Deduct from Source → Add to Transit while Draft"""
    #     transit_wh = self.custom_transit_warehouse
    #     if not transit_wh:
    #         frappe.throw(_("Please set the Transit Warehouse."))

    #     for item in self.items:
    #         if not item.s_warehouse:
    #             frappe.throw(_("Source warehouse missing for item {0}").format(item.item_code))

    #         self._make_sl_entry(item, item.s_warehouse, -item.qty)
    #         self._make_sl_entry(item, transit_wh, item.qty)

    #     frappe.msgprint(_("Stock moved from Source to Transit."))

    # def complete_transfer(self):
    #     """Deduct from Transit → Add to Target on Submit"""
    #     transit_wh = self.custom_transit_warehouse
    #     if not transit_wh:
    #         frappe.throw(_("Please set the Transit Warehouse."))

    #     for item in self.items:
    #         if not item.t_warehouse:
    #             frappe.throw(_("Target warehouse missing for item {0}").format(item.item_code))

    #         self._make_sl_entry(item, transit_wh, -item.qty)
    #         self._make_sl_entry(item, item.t_warehouse, item.qty)

    #     frappe.msgprint(_("Stock moved from Transit to Target. Transfer Completed."))

    # def _make_sl_entry(self, item, warehouse, qty):
    #     """Directly insert Stock Ledger Entry (works in v15 without make_sl_entries)"""
    #     sle = frappe.get_doc({
    #         "doctype": "Stock Ledger Entry",
    #         "item_code": item.item_code,
    #         "warehouse": warehouse,
    #         "actual_qty": qty,
    #         "voucher_type": "Stock Entry",
    #         "voucher_no": self.name,
    #         "posting_date": self.posting_date,
    #         "posting_time": self.posting_time,
    #         "company": self.company,
    #         "stock_uom": item.uom,
    #     })
    #     sle.insert(ignore_permissions=True)
    

    # Modified for Item Group-Based Inventory
    def get_gl_entries(self, warehouse_account):
        enabled = frappe.db.get_value(
            "Company",
            self.company,
            "custom_enable_item_group_based_inventory"
        )
        if not enabled:
            return super().get_gl_entries(
                warehouse_account
            )
        if self.purpose in ("Manufacture", "Disassemble", "Repack"):

            warehouse_account = self.get_item_group_warehouse_account_map(
                warehouse_account
            )

            gl_entries = super().get_gl_entries(
                warehouse_account
            )

            return process_gl_map(
                gl_entries,
                from_repost=frappe.flags.through_repost_item_valuation
            )

        elif self.purpose == "Material Receipt":

            gl_entries = self.get_item_group_material_receipt_gl_entries()

        elif self.purpose in("Material Issue", "Material Consumption for Manufacture", "Send to Subcontractor"):

            gl_entries = self.get_item_group_material_issue_gl_entries()
        
        elif self.purpose == "Material Transfer for Manufacture":
            gl_entries = []
            for item in self.items:
                if not item.s_warehouse or not item.t_warehouse:
                    continue

                inventory_account = self.get_item_group_account(item.item_code)
                expense_account = item.expense_account
                if not expense_account:
                    expense_account = frappe.db.get_value(
                        "Company",
                        self.company,
                        "default_expense_account"
                    )
                if not expense_account:
                    frappe.throw(
                        f"Missing Expense Account for Item {item.item_code}"
                    )
                amount = flt(item.basic_amount or item.amount)

                if amount <= 0:
                    continue

                # 1. Target Side: Debit the Item Group Inventory Account
                gl_entries.append(self.get_gl_dict({
                    "account": inventory_account,
                    "against": expense_account,
                    "debit": amount,
                    "credit": 0,
                    "cost_center": item.cost_center,
                    "remarks": self.remarks or _("Material Transfer for Manufacture")
                }, item=item))

                # 2. Source Side: Credit the Stock Adjustment / Expense Account (e.g., 5119)
                gl_entries.append(self.get_gl_dict({
                    "account": expense_account,
                    "against": inventory_account,
                    "debit": 0,
                    "credit": amount,
                    "cost_center": item.cost_center,
                    "remarks": self.remarks or _("Material Transfer for Manufacture")
                }, item=item))

        else:
            gl_entries = super().get_gl_entries(
                warehouse_account
            )

        return process_gl_map(
            gl_entries,
            from_repost=frappe.flags.through_repost_item_valuation
        )
    
    def get_item_group_account(self, item_code):
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
                Missing Inventory Account <br/>
                Item:
                {item_code}
                Item Group:
                {item_group}
                """
            )

        return account
    
     # Material Receipt
    def get_item_group_material_receipt_gl_entries(self):
        gl_entries = []
        for item in self.items:
            if not item.t_warehouse:
                continue
            account = self.get_item_group_account(
                item.item_code
            )
            if not account:
                continue
            amount = flt(item.basic_amount)
            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": account,
                        "against": item.expense_account,
                        "debit": amount,
                        "credit": 0,
                        "cost_center": item.cost_center,
                        "remarks": self.remarks or _("Stock Entry")
                    },
                    item=item
                )
            )
            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": item.expense_account,
                        "against": account,
                        "debit": 0,
                        "credit": amount,
                        "cost_center": item.cost_center,
                        "remarks": self.remarks or _("Stock Entry")
                    },
                    item=item
                )
            )

        return gl_entries
    
    # "Material Issue", "Material Consumption for Manufacture", "Send to Subcontractor"
    def get_item_group_material_issue_gl_entries(self):

        gl_entries = []

        for item in self.items:
            if not item.s_warehouse:
                continue
            account = self.get_item_group_account(
                item.item_code
            )

            amount = flt(item.basic_amount)
            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": item.expense_account,
                        "against": account,
                        "debit": amount,
                        "credit": 0,
                        "cost_center": item.cost_center,
                        "remarks": self.remarks or _("Stock Entry")
                    },
                    item=item
                )
            )
            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": account,
                        "against": item.expense_account,
                        "debit": 0,
                        "credit": amount,
                        "cost_center": item.cost_center,
                        "remarks": self.remarks or _("Stock Entry")
                    },
                    item=item
                )
            )

        return gl_entries

     # Manufacture, and Disassemble
    def get_item_group_warehouse_account_map(self, warehouse_account):
        new_map = {}

        for warehouse, account_data in warehouse_account.items():

            # keep structure
            new_map[warehouse] = account_data.copy()

        for item in self.items:

            account = self.get_item_group_account(
                item.item_code
            )

            if item.t_warehouse:
                if item.t_warehouse in new_map:
                    new_map[item.t_warehouse]["account"] = account

            if item.s_warehouse:
                if item.s_warehouse in new_map:
                    new_map[item.s_warehouse]["account"] = account

        return new_map


    
