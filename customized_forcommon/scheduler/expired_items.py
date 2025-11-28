import frappe
from frappe.utils import getdate, nowdate
from frappe import _

def mark_expired_batches():
    """
    Detect expired batches and move stock to Expired Warehouse automatically.
    UPDATED FOR SERIAL AND BATCH BUNDLE SYSTEM
    """
    today = getdate()

    # 1️⃣ Get Expired Warehouse from Stock Settings
    expired_wh = frappe.db.get_single_value("Stock Settings", "expired_warehouse")
    if not expired_wh:
        frappe.log_error("Expired Warehouse NOT configured in Stock Settings", "Expired Batch Scheduler")
        return

    # 2️⃣ Get all active batches that have expired
    expired_batches = frappe.get_all(
        "Batch",
        filters={
            "expiry_date": ["<=", today],
            "disabled": 0
        },
        fields=["name", "item"]
    )

    if not expired_batches:
        frappe.logger().info("No expired batches found to process")
        return

    moved_batches = 0
    failed_batches = []

    for batch in expired_batches:
        item_code = batch.item
        batch_no = batch.name

        try:
            # 3️⃣ ✅ UPDATED: Get stock from Serial and Batch Bundles
            stock_locations = frappe.db.sql("""
                SELECT sbb.warehouse, SUM(sbb_entry.qty) as qty
                FROM `tabSerial and Batch Bundle` sbb
                INNER JOIN `tabSerial and Batch Entry` sbb_entry ON sbb.name = sbb_entry.parent
                WHERE sbb.item_code = %s
                    AND sbb_entry.batch_no = %s
                    AND sbb.docstatus = 1
                    AND sbb.is_cancelled = 0
                GROUP BY sbb.warehouse
                HAVING SUM(sbb_entry.qty) > 0
            """, (item_code, batch_no), as_dict=True)

            if not stock_locations:
                # No stock found, just disable the batch
                frappe.db.set_value("Batch", batch_no, "disabled", 1)
                continue

            # 4️⃣ Create stock entries for each warehouse with stock
            stock_entries_created = 0

            for location in stock_locations:
                source_wh = location.warehouse
                qty = location.qty

                if source_wh == expired_wh or qty <= 0:
                    continue

                # Create Stock Entry
                se = frappe.get_doc({
                    "doctype": "Stock Entry",
                    "purpose": "Material Transfer",
                    "stock_entry_type": "Material Transfer",
                    "posting_date": today,
                    "posting_time": nowdate(),
                    "items": [{
                        "item_code": item_code,
                        "qty": qty,
                        "s_warehouse": source_wh,
                        "t_warehouse": expired_wh,
                        "batch_no": batch_no,
                        "allow_alternative_item": 0
                    }]
                })

                se.insert(ignore_permissions=True)
                se.submit()
                stock_entries_created += 1

                frappe.db.commit()  # Commit after each successful SE

            # 5️⃣ Only disable batch if stock was successfully moved
            if stock_entries_created > 0:
                frappe.db.set_value("Batch", batch_no, "disabled", 1)
                moved_batches += 1

                # Log success
                frappe.logger().info(
                    f"Successfully moved batch {batch_no} ({item_code}) "
                    f"to expired warehouse {expired_wh}"
                )

        except Exception as e:
            frappe.db.rollback()
            error_msg = f"Failed to process batch {batch_no}: {str(e)}"
            failed_batches.append(batch_no)
            frappe.log_error(error_msg, "Expired Batch Scheduler")

    # 6️⃣ Final summary
    summary = f"Expired batches processed: {moved_batches} moved, {len(failed_batches)} failed"
    frappe.logger().info(summary)

    if failed_batches:
        frappe.log_error(f"Failed batches: {', '.join(failed_batches)}", "Expired Batch Scheduler")