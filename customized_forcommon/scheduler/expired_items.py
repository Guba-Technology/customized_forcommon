import frappe
from frappe.utils import getdate, nowdate, now_datetime, time_diff_in_seconds
from frappe import _

def mark_expired_batches():
    """
    Detect expired batches and move stock to Expired Warehouse automatically.
    UPDATED FOR SERIAL AND BATCH BUNDLE SYSTEM
    """
    print("mark_expired_batches() started")

    today = getdate()
    print(f"Today's date: {today}")

    # Get Expired Warehouse from Stock Settings
    expired_wh = frappe.db.get_single_value("Stock Settings", "expired_warehouse")
    print(f"Expired Warehouse: {expired_wh}")

    if not expired_wh:
        frappe.log_error("Expired Warehouse NOT configured in Stock Settings", "Expired Batch Scheduler")
        print(" No expired warehouse configured, exiting")
        return

    # Get all active batches that have expired
    expired_batches = frappe.get_all(
        "Batch",
        filters={
            "expiry_date": ["<=", today],
            "disabled": 0
        },
        fields=["name", "item"]
    )

    print(f"Found {len(expired_batches)} expired batches")

    if not expired_batches:
        frappe.logger().info("No expired batches found to process")
        print(" No expired batches found, exiting")
        return

    moved_batches = 0
    failed_batches = []

    for batch in expired_batches:
        item_code = batch.item
        batch_no = batch.name
        print(f" Processing batch {batch_no} for item {item_code}")

        try:
            # Get stock from Serial and Batch Bundles
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

            print(f"  Stock locations found: {len(stock_locations)}")

            if not stock_locations:
                # No stock found, just disable the batch
                frappe.db.set_value("Batch", batch_no, "disabled", 1)
                print(f" No stock found. Batch {batch_no} disabled")
                continue

            # Create stock entries for each warehouse with stock
            stock_entries_created = 0

            for location in stock_locations:
                source_wh = location.warehouse
                qty = location.qty

                if source_wh == expired_wh or qty <= 0:
                    print(f"  ⏭ Skipping warehouse {source_wh} with qty {qty}")
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
                print(f" Moved {qty} of {item_code} from {source_wh} to {expired_wh}")

                frappe.db.commit()

            # Only disable batch if stock was successfully moved
            if stock_entries_created > 0:
                frappe.db.set_value("Batch", batch_no, "disabled", 1)
                moved_batches += 1
                print(f" Batch {batch_no} disabled after stock movement")

        except Exception as e:
            frappe.db.rollback()
            error_msg = f"Failed to process batch {batch_no}: {str(e)}"
            failed_batches.append(batch_no)
            frappe.log_error(error_msg, "Expired Batch Scheduler")
            print(f" {error_msg}")

    # Final summary
    summary = f"Expired batches processed: {moved_batches} moved, {len(failed_batches)} failed"
    frappe.logger().info(summary)
    print(f" {summary}")

    if failed_batches:
        frappe.log_error(f"Failed batches: {', '.join(failed_batches)}", "Expired Batch Scheduler")
        print(f" Failed batches: {', '.join(failed_batches)}")
