# custom_material/overrides/material_request.py

from erpnext.selling.doctype.customer.customer import Customer as BaseCustomer
import frappe

class CustomCustomer(BaseCustomer):
    def validate(self):
        self.add_customer_type()
        super().validate()

    def add_customer_type(self):
        if self.customer_type == "Foreign" or  self.customer_type == "Local":
            meta = frappe.get_meta("Customer")
            field = meta.get_field("customer_type")
            if field and "Foreign" not in field.options.split("\n"):
                field.options += "\nForeign"
            if field and "Local" not in field.options.split("\n"):
                field.options += "\nLocal"
