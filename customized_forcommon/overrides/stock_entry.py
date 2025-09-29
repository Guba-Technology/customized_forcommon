import frappe
from frappe import _
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry as ERPNextStockEntry

class CustomStockEntry(ERPNextStockEntry):

    def on_update(self):
        """Handle Draft → In Transit (docstatus = 0)"""
        if self.stock_entry_type != "Material Transfer":
            super().on_update()  # only call default logic for other types
            return

        if self.docstatus == 0 and self.custom_transfer_status == "In Transit":
            self.send_to_transit()

    def on_submit(self):
        """Handle In Transit → Completed (docstatus = 1)"""
        if self.stock_entry_type != "Material Transfer":
            super().on_submit()  # only call default logic for other types
            return

        if self.custom_transfer_status == "Completed":
            self.complete_transfer()

    def send_to_transit(self):
        """Deduct from Source → Add to Transit while Draft"""
        transit_wh = self.custom_transit_warehouse
        if not transit_wh:
            frappe.throw(_("Please set the Transit Warehouse."))

        for item in self.items:
            if not item.s_warehouse:
                frappe.throw(_("Source warehouse missing for item {0}").format(item.item_code))

            self._make_sl_entry(item, item.s_warehouse, -item.qty)
            self._make_sl_entry(item, transit_wh, item.qty)

        frappe.msgprint(_("Stock moved from Source to Transit."))

    def complete_transfer(self):
        """Deduct from Transit → Add to Target on Submit"""
        transit_wh = self.custom_transit_warehouse
        if not transit_wh:
            frappe.throw(_("Please set the Transit Warehouse."))

        for item in self.items:
            if not item.t_warehouse:
                frappe.throw(_("Target warehouse missing for item {0}").format(item.item_code))

            self._make_sl_entry(item, transit_wh, -item.qty)
            self._make_sl_entry(item, item.t_warehouse, item.qty)

        frappe.msgprint(_("Stock moved from Transit to Target. Transfer Completed."))

    def _make_sl_entry(self, item, warehouse, qty):
        """Directly insert Stock Ledger Entry (works in v15 without make_sl_entries)"""
        sle = frappe.get_doc({
            "doctype": "Stock Ledger Entry",
            "item_code": item.item_code,
            "warehouse": warehouse,
            "actual_qty": qty,
            "voucher_type": "Stock Entry",
            "voucher_no": self.name,
            "posting_date": self.posting_date,
            "posting_time": self.posting_time,
            "company": self.company,
            "stock_uom": item.uom,
        })
        sle.insert(ignore_permissions=True)
