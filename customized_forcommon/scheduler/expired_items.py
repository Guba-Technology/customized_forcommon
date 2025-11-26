import frappe
from frappe.utils import nowdate

def mark_expired_items():
    """Detect expired items, update status, and move stock to expired warehouse."""
    today = nowdate()

    # 1️⃣ Get expired warehouse from Stock Settings
    expired_wh = frappe.db.get_single_value("Stock Settings", "expired_warehouse")
    if not expired_wh:
        frappe.log_error("Expired Warehouse NOT configured in Stock Settings", "Expired Item Scheduler")
        return

    # 2️⃣ Find all Purchase Receipt Items that have expired
    expired_pr_items = frappe.get_all(
        "Purchase Receipt Item",
        filters={
            "item_end_date": ["<=", today]
        },
        fields=["item_code", "warehouse", "parent"]
    )

    for row in expired_pr_items:
        item = row.item_code

        # 3️⃣ Update Item Status
        frappe.db.set_value("Item", item, "item_status", "Expired")

        # 4️⃣ Move stock using Stock Entry (proper ERPNext method)
        qty = frappe.db.get_value("Bin",
            {"item_code": item, "warehouse": row.warehouse},
            "actual_qty"
        )

        if qty and qty > 0 and row.warehouse != expired_wh:

            # Create a Stock Entry to move stock
            se = frappe.get_doc({
                "doctype": "Stock Entry",
                "stock_entry_type": "Material Transfer",
                "from_warehouse": row.warehouse,
                "to_warehouse": expired_wh,
                "items": [{
                    "item_code": item,
                    "qty": qty
                }]
            })
            se.insert(ignore_permissions=True)
            se.submit()

    frappe.db.commit()
