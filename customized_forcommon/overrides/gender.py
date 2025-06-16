from frappe.contacts.doctype.gender.gender import Gender
import frappe
from frappe import _

class CustomGender(Gender):
    def validate(self):
        if hasattr(super(), "validate"):
            super().validate()
        self.restrict_to_create_gender()

    def restrict_to_create_gender(self):
        allowed_genders = ["Male", "Female"]
        if self.gender not in allowed_genders:
            frappe.throw(f"You can only create gender 'Male' or 'Female'. You tried to create '{self.gender}'")
