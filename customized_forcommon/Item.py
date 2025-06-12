import frappe

def custom_item_autoname(doc, method):
    new_name = f"{doc.item_code}-{doc.item_name}"

    if doc.is_new():
        # Set name only if creating
        doc.name = new_name
    else:
        # Check if item_code or item_name changed, and rename if needed
        old_doc = frappe.get_doc("Item", doc.name)
        old_name = f"{old_doc.item_code}-{old_doc.item_name}"

        if new_name != old_name and not frappe.db.exists("Item", new_name):
            frappe.rename_doc("Item", doc.name, new_name, force=True)
