from erpnext.manufacturing.doctype.bom_creator.bom_creator import BOM_FIELDS, BOM_ITEM_FIELDS, BOMCreator
import frappe

# Add custom field
BOM_ITEM_FIELDS.append("operation")

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
        bom.update(
            {
                "item": row.item_code,
                "bom_type": "Production",
                "quantity": row.qty,
                "allow_alternative_item": 1,
                "bom_creator": self.name,
                "bom_creator_item": bom_creator_item,
            }
        )

        if row.item_code == self.item_code and (self.routing or self.has_operations()):
            bom.routing = self.routing
            bom.with_operations = 1
            bom.transfer_material_against = "Work Order"

        for field in BOM_FIELDS:
            if self.get(field):
                bom.set(field, self.get(field))

        for item in production_item_wise_rm[(row.item_code, row.name)]["items"]:
            bom_no = ""
            item.do_not_explode = 1
            if (item.item_code, item.name) in production_item_wise_rm:
                bom_no = production_item_wise_rm.get((item.item_code, item.name)).bom_no
                item.do_not_explode = 0

            item_args = {field: item.get(field) for field in BOM_ITEM_FIELDS}
            item_args.update(
                {
                    "bom_no": bom_no,
                    "allow_alternative_item": 1,
                    "allow_scrap_items": 1,
                    "include_item_in_manufacturing": 1,
                }
            )
            bom.append("items", item_args)

        bom.save(ignore_permissions=True)
        bom.submit()

        production_item_wise_rm[(row.item_code, row.name)].bom_no = bom.name

    def has_operations(self):
        return any(row.operation for row in self.items)
