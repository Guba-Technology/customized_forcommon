# custom_material/overrides/material_request.py

from erpnext.stock.doctype.material_request.material_request import MaterialRequest as ERPNextMaterialRequest
import frappe

class CustomMaterialRequest(ERPNextMaterialRequest):
    def before_validate(self):
        self._allow_custom_request_type()
        super().before_validate()

    def _allow_custom_request_type(self):
        if self.material_request_type == "Material Cost":
            meta = frappe.get_meta("Material Request")
            field = meta.get_field("material_request_type")
            if field and "Material Cost" not in field.options.split("\n"):
                field.options += "\nMaterial Cost"
