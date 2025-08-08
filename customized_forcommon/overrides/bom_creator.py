from erpnext.manufacturing.doctype.bom_creator.bom_creator import BOM_FIELDS, BOM_ITEM_FIELDS
from erpnext.manufacturing.doctype.bom_creator.bom_creator import BOMCreator
import frappe
import traceback

class CustomBom(BOMCreator):
    def create_bom(self, row, production_item_wise_rm):
        bom_creator_item = row.name if row.name != self.name else ""

        if frappe.db.exists(
            "BOM",
            {
                "bom_creator": self.name,
                "item": row.item_code,
                "bom_creator_item": bom_creator_item,
                "docstatus": 1,
            },
        ):
            return

        bom = frappe.new_doc("BOM")
        bom.update({
            "item": row.item_code,
            "bom_type": "Production",
            "quantity": row.qty or 0,
            "allow_alternative_item": 1,
            "bom_creator": self.name,
            "bom_creator_item": bom_creator_item,
        })

        if row.item_code == self.item_code and (self.routing or self.has_operations()):
            bom.routing = self.routing
            bom.with_operations = 1
            bom.transfer_material_against = "Work Order"

        for field in BOM_FIELDS:
            val = self.get(field)
            if val is not None:
                bom.set(field, val)

        for item in production_item_wise_rm.get((row.item_code, row.name), {}).get("items", []):
            if not item.get("item_code") or not item.get("qty") or not item.get("uom"):
                frappe.log_error(
                    message=f"Skipping BOM item due to missing required fields: {item.as_dict() if hasattr(item, 'as_dict') else item}",
                    title="Invalid BOM Item in create_bom"
                )
                continue

            bom_no = ""
            item.do_not_explode = 1

            if (item.item_code, item.name) in production_item_wise_rm:
                bom_no = production_item_wise_rm.get((item.item_code, item.name)).bom_no
                item.do_not_explode = 0

            item_args = {field: item.get(field) for field in BOM_ITEM_FIELDS}
            item_args.update({
                "bom_no": bom_no,
                "allow_alternative_item": 1,
                "allow_scrap_items": 1,
                "include_item_in_manufacturing": 1,
            })

            bom.append("items", item_args)

        try:
            bom.save(ignore_permissions=True)
            bom.submit()
            production_item_wise_rm[(row.item_code, row.name)].bom_no = bom.name
        except Exception:
            traceback_str = traceback.format_exc()
            frappe.log_error(traceback_str, f"Failed to create BOM for item {row.item_code}")
            frappe.throw(f"Failed to create BOM for item {row.item_code}: {traceback_str}")
