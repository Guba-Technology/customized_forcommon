# Copyright (c) 2025, Guba Technology and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Agreement(Document):
    def validate(self):
        self.validate_duplicate_items()

    def validate_duplicate_items(self):
        """Prevent duplicate item_code entries in Agreement Item child table."""
        seen = set()
        duplicates = []

        for item in self.agreement_item:
            if item.item_code in seen:
                duplicates.append(item.item_code)
            else:
                seen.add(item.item_code)

        if duplicates:
            frappe.throw(
                f"Duplicate items found in Agreement Items: {', '.join(set(duplicates))}"
            )
