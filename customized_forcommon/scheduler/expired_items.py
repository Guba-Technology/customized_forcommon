# import frappe
# from frappe.utils import getdate, nowdate, nowtime
# from frappe import _

# def mark_expired_batches():
#     """
#     Detect expired batches and move stock to Expired Warehouse automatically.
#     Updated for Serial and Batch Bundle system.
#     """
#     today = getdate()

#     # Get Expired Warehouse from Stock Settings
#     expired_wh = frappe.db.get_single_value("Stock Settings", "expired_warehouse")
#     if not expired_wh:
#         frappe.log_error("Expired Warehouse NOT configured in Stock Settings", "Expired Batch Scheduler")
#         return

#     # Get all active batches that have expired
#     expired_batches = frappe.get_all(
#         "Batch",
#         filters={
#             "expiry_date": ["<=", today],
#             # "disabled": 0
#         },
#         fields=["name", "item"]
#     )

#     if not expired_batches:
#         frappe.logger().info("No expired batches found to process")
#         return

#     moved_batches = 0
#     failed_batches = []

#     for batch in expired_batches:
#         item_code = batch.item
#         batch_no = batch.name

#         try:
#             # Get stock from Serial and Batch Bundles
#             stock_locations = frappe.db.sql("""
#                 SELECT sbb.warehouse, SUM(sbb_entry.qty) as qty
#                 FROM `tabSerial and Batch Bundle` sbb
#                 INNER JOIN `tabSerial and Batch Entry` sbb_entry ON sbb.name = sbb_entry.parent
#                 WHERE sbb.item_code = %s
#                     AND sbb_entry.batch_no = %s
#                     AND sbb.docstatus = 1
#                     AND sbb.is_cancelled = 0
#                 GROUP BY sbb.warehouse
#                 HAVING SUM(sbb_entry.qty) > 0
#             """, (item_code, batch_no), as_dict=True)

#             # If no stock exists, just disable the batch
#             if not stock_locations:
#                 frappe.db.set_value("Batch", batch_no, "disabled", 1)
#                 frappe.logger().info(f"No stock found for batch {batch_no}. Batch disabled.")
#                 continue

#             stock_entries_created = 0

#             for location in stock_locations:
#                 source_wh = location.warehouse
#                 qty = location.qty

#                 # Skip if source is already expired warehouse or qty <= 0
#                 if source_wh == expired_wh or qty <= 0:
#                     continue

#                 # Create Stock Entry for Material Transfer
#                 se = frappe.get_doc({
#                     "doctype": "Stock Entry",
#                     "purpose": "Material Transfer",
#                     "stock_entry_type": "Material Transfer",
#                     "posting_date": today,
#                     "posting_time": nowtime(),
#                     "items": [{
#                         "item_code": item_code,
#                         "qty": qty,
#                         "s_warehouse": source_wh,
#                         "t_warehouse": expired_wh,
#                         "batch_no": batch_no,
#                         "allow_alternative_item": 0
#                     }]
#                 })

#                 se.insert(ignore_permissions=True)
#                 se.submit()
#                 stock_entries_created += 1
#                 frappe.logger().info(f"Stock Entry created for batch {batch_no}: {qty} from {source_wh} -> {expired_wh}")

#             # Disable batch only if stock was moved
#             if stock_entries_created > 0:
#                 frappe.db.set_value("Batch", batch_no, "disabled", 1)
#                 moved_batches += 1

#         except Exception as e:
#             frappe.db.rollback()
#             failed_batches.append(batch_no)
#             frappe.log_error(f"Failed to process batch {batch_no}: {str(e)}", "Expired Batch Scheduler")

#     # Final summary
#     summary = f"Expired batches processed: {moved_batches} moved, {len(failed_batches)} failed"
#     frappe.logger().info(summary)
#     if failed_batches:
#         frappe.log_error(f"Failed batches: {', '.join(failed_batches)}", "Expired Batch Scheduler")
