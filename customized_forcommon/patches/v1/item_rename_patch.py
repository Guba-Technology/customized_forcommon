import frappe

def execute():
    items = frappe.get_all("Item", fields=["name", "item_code", "item_name"])

    for i in items:
        item_code = i.item_code or ""
        item_name = i.item_name or ""
        new_name = f"{item_code}-{item_name}".strip("-")

        # Skip if name is already correct
        if i.name == new_name:
            continue

        # Skip if new name already exists
        if frappe.db.exists("Item", new_name):
            continue

        try:
            frappe.rename_doc("Item", i.name, new_name, force=True)
        except Exception:
            # Optional: continue on error silently
            continue
