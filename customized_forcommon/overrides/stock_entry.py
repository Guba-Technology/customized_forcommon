import frappe
from frappe import _
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry as ERPNextStockEntry
from frappe.utils import flt

class CustomStockEntry(ERPNextStockEntry):
    def after_insert(self):
        if self.stock_entry_type == "Material Issue for Transfer":
            self.create_material_receipt_from_issue()  # create Material Receipt for Transfer on creation of Material Issue for Transfer
    def on_update(self):
        """Handle Draft → In Transit (docstatus = 0)"""
        # if self.stock_entry_type != "Material Transfer":
        #     super().on_update()  # only call default logic for other types
        #     return
        super().on_update()  
        # if self.docstatus == 0 and self.custom_transfer_status == "In Transit":
        #     self.send_to_transit()
        # copy this document to Material Receipt for Transfer doctype
        # set reference_document to this document name
        if self.stock_entry_type == "Material Issue for Transfer":
            self.create_material_receipt_from_issue()

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

    def create_material_receipt_from_issue(self):
        existing_name = frappe.db.get_value("Material Receipt for Transfer", 
            {"reference_document": self.name}, "name")

        # Deep copy to prevent modifying the current Stock Entry object in memory
        source_data = self.as_dict()
        
        exclude = [
            "name", "docstatus", "owner", "creation", "modified", 
            "modified_by", "amended_from", "amendment_date", "idx"
        ]
        
        for field in exclude:
            source_data.pop(field, None)

        # Clean the child table items to remove parent, parentfield, and parenttype
        # This ensures they are treated as new rows for the target DocType
        if "items" in source_data:
            for item in source_data["items"]:
                item.pop("name", None)
                item.pop("parent", None)
                item.pop("parentfield", None)
                item.pop("parenttype", None)

        if existing_name:
            doc = frappe.get_doc("Material Receipt for Transfer", existing_name)
            if doc.docstatus == 0:
                doc.update(source_data)
                doc.purpose = "Material Receipt for Transfer"
                doc.reference_document = self.name
                
                doc.set("remark_list", [])
                for item in doc.items:
                    doc.append("remark_list", {
                        "item": item.item_code,
                        "qty": item.qty,
                    })
                doc.save()
            return doc
        else:
            new_doc = frappe.new_doc("Material Receipt for Transfer")
            new_doc.update(source_data)
            
            new_doc.name = None
            new_doc.purpose = "Material Receipt for Transfer"
            new_doc.reference_document = self.name
            
            new_doc.set("remark_list", [])
            for item in new_doc.items:
                new_doc.append("remark_list", {
                    "item": item.item_code,
                    "qty": item.qty
                })
                
            return new_doc.insert()
    

    