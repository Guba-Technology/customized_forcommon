from erpnext.selling.doctype.sales_order.sales_order import SalesOrder as ERPNextSalesOrder
import frappe
from frappe import _

class CustomSalesOrder(ERPNextSalesOrder):
    def validate(self):
        self._allow_custom_order_type()
        super().validate()
        self.validate_item_quantity()

    def _allow_custom_order_type(self):
        if self.order_type == "Manufactured Sale":
            meta = frappe.get_meta("Sales Order")
            field = meta.get_field("order_type")
            if field and "Manufactured Sale" not in field.options.split("\n"):
                field.options += "\nManufactured Sale"
    def validate_item_quantity(self):
        selling_settings = frappe.get_doc("Selling Settings")
        if selling_settings.allow_zero_qty_in_sales_order:
            return
        else:
            for item in self.items:
                if item.qty <= 0:
                    frappe.throw(_("Quantity must be greater than zero for item {0}").format(item.item_code))