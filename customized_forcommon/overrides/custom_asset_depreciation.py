import frappe
from erpnext.assets.doctype.asset import asset

original_method = asset.make_new_active_asset_depr_schedules_and_cancel_current_ones

def custom_make_new_active_asset_depr_schedules_and_cancel_current_ones(asset_doc, notes, date_of_disposal=None):
    # First, let ERPNext create schedules normally
    original_method(asset_doc, notes, date_of_disposal)

    # Patch each schedule to use custom_cost_basis
    for fb in asset_doc.get("finance_books") or []:
        if not getattr(fb, "custom_cost_basis", 0):
            continue

        ads_name = frappe.db.get_value(
            "Asset Depreciation Schedule",
            {"asset": asset_doc.name, "finance_book": fb.finance_book},
        )
        if not ads_name:
            continue

        ads_doc = frappe.get_doc("Asset Depreciation Schedule", ads_name)

        for row in ads_doc.get("depreciation_schedule") or []:
            rate = fb.rate_of_depreciation or 0
            row.depreciation_amount = round(fb.custom_cost_basis * (rate / 100), 2)
            row.db_update()

        # Update the total value after depreciation in finance book
        fb.value_after_depreciation = fb.custom_cost_basis
        fb.db_update()

        # Save the schedule doc to commit changes
        ads_doc.save()

        frappe.logger().info(
            f"Patched depreciation for Asset {asset_doc.name}, Finance Book {fb.finance_book}"
        )

# Patch ERPNext method
asset.make_new_active_asset_depr_schedules_and_cancel_current_ones = custom_make_new_active_asset_depr_schedules_and_cancel_current_ones
