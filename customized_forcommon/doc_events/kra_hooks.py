import frappe
import re

def auto_increment_kra_number(doc, method):
    # Get the highest existing number
    last_kra = frappe.db.get_all(
        "KRA",
        fields=["custom_label_number"],
        filters={"custom_label_number": ["is", "set"]},
        order_by="custom_label_number desc",
        limit=1
    )

    next_number = 1
    if last_kra:
        last_label = last_kra[0].custom_label_number
        match = re.match(r"KRA-(\d+)", last_label)
        if match:
            try:
                next_number = int(match.group(1)) + 1
            except ValueError:
                pass

   
    doc.custom_label_number = f"KRA-{next_number:05d}"

