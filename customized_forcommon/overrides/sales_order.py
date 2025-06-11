from erpnext.selling.doctype.sales_order.sales_order import SalesOrder as ERPNextSalesOrder
import frappe
from frappe import _

class CustomSalesOrder(ERPNextSalesOrder):
    def validate(self):
        self._allow_custom_order_type()
        super().validate()

    def _allow_custom_order_type(self):
        if self.order_type == "Manufactured Sale":
            meta = frappe.get_meta("Sales Order")
            field = meta.get_field("order_type")
            if field and "Manufactured Sale" not in field.options.split("\n"):
                field.options += "\nManufactured Sale"
