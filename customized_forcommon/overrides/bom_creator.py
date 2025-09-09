import frappe
from erpnext.manufacturing.doctype.bom_creator.bom_creator import (
    BOM_FIELDS, BOM_ITEM_FIELDS, BOMCreator, get_item_details, get_parent_row_no
)

# Add custom field globally (monkey patch style)
if "operation" not in BOM_ITEM_FIELDS:
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


@frappe.whitelist()
def get_children(doctype=None, parent=None, **kwargs):
    if isinstance(kwargs, str):
        kwargs = frappe.parse_json(kwargs)
    if isinstance(kwargs, dict):
        kwargs = frappe._dict(kwargs)

    fields = [
        "item_code as value",
        "item_name as title",
        "is_expandable as expandable",
        "parent as parent_id",
        "qty",
        "idx",
        "'BOM Creator Item' as doctype",
        "name",
        "uom",
        "rate",
        "amount",
        "operation",
        "is_subcontracted",
    ]

    query_filters = {
        "fg_item": parent,
        "parent": kwargs.parent_id,
    }

    if kwargs.name:
        query_filters["name"] = kwargs.name

    return frappe.get_all("BOM Creator Item", fields=fields, filters=query_filters, order_by="idx")


@frappe.whitelist()
def add_sub_assembly(**kwargs):
    if isinstance(kwargs, str):
        kwargs = frappe.parse_json(kwargs)
    if isinstance(kwargs, dict):
        kwargs = frappe._dict(kwargs)

    doc = frappe.get_doc("BOM Creator", kwargs.parent)
    bom_item = frappe.parse_json(kwargs.bom_item)

    name = kwargs.fg_reference_id
    parent_row_no = ""

    if not kwargs.convert_to_sub_assembly:
        item_info = get_item_details(bom_item.item_code)
        parent_row_no = get_parent_row_no(doc, kwargs.fg_reference_id)

        item_row = doc.append(
            "items",
            {
                "item_code": bom_item.item_code,
                "qty": bom_item.qty,
                "uom": item_info.stock_uom,
                "fg_item": kwargs.fg_item,
                "conversion_factor": 1,
                "parent_row_no": parent_row_no,
                "fg_reference_id": name,
                "stock_qty": bom_item.qty,
                "do_not_explode": 1,
                "is_expandable": 1,
                "stock_uom": item_info.stock_uom,
                "operation": bom_item.operation,
            },
        )

        parent_row_no = item_row.idx
        name = ""
    else:
        parent_row_no = get_parent_row_no(doc, kwargs.fg_reference_id)

    for row in bom_item.get("items"):
        row = frappe._dict(row)
        item_info = get_item_details(row.item_code)
        doc.append(
            "items",
            {
                "item_code": row.item_code,
                "qty": row.qty,
                "operation": row.operation,
                "fg_item": bom_item.item_code,
                "uom": item_info.stock_uom,
                "fg_reference_id": name,
                "parent_row_no": parent_row_no,
                "conversion_factor": 1,
                "do_not_explode": 1,
                "stock_qty": row.qty,
                "stock_uom": item_info.stock_uom,
            },
        )

    doc.save()
    return doc
