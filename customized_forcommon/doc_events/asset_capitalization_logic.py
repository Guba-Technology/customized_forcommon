import frappe
from frappe import _
from erpnext.assets.doctype.asset.asset import get_asset_value_after_depreciation, get_depr_schedule

def update_child_table_after_capitalization(doc, method):
    """
    Hook: on_submit of Asset Capitalization
    Calculate accumulated depreciation and number of booked depreciations after capitalization
    and update child table fields in Asset.
    """
    try:
        # Check if this is an Asset Capitalization document
        if doc.doctype != "Asset Capitalization":
            return

        asset = frappe.get_doc("Asset", doc.asset)

        # Calculate accumulated depreciation using available functions
        accumulated_amount, num_booked = get_accumulated_depreciation_for_asset(asset.name)

        # Append a new row in the child table
        asset.append("capitalization_details", {
            "date_of_capitalization": doc.posting_date or frappe.utils.nowdate(),
            "depreciation_start_date": asset.depreciation_start_date,
            "opening_accumulated_d": accumulated_amount,
            "opening_number_o": num_booked
        })

        # Set the custom fields to match built-in fields
        asset.opening_accumulated = getattr(asset, 'opening_accumulated_depreciation', 0) or 0
        asset.opening_number = getattr(asset, 'opening_number_of_booked_depreciations', 0) or 0

        asset.save(ignore_permissions=True)
        frappe.db.commit()

        frappe.msgprint(_("Asset capitalization details updated successfully"))

    except Exception as e:
        frappe.log_error(f"Error in update_child_table_after_capitalization: {str(e)}")
        frappe.throw(_("Failed to update asset capitalization details: {0}").format(str(e)))

def sync_custom_fields(doc, method):
    """
    Hook: before_save of Asset
    Sync custom fields with built-in fields automatically
    """
    try:
        # Only proceed if this is an Asset document
        if doc.doctype != "Asset":
            return

        # Get values from built-in fields (with safe defaults)
        builtin_accumulated = getattr(doc, 'opening_accumulated_depreciation', 0) or 0
        builtin_number = getattr(doc, 'opening_number_of_booked_depreciations', 0) or 0

        # Sync custom fields with built-in fields
        doc.opening_accumulated = builtin_accumulated
        doc.opening_number = builtin_number

        # No need to call save() here since this is a before_save hook

    except Exception as e:
        frappe.log_error(f"Error in sync_custom_fields: {str(e)}")

# Keep the other functions (get_accumulated_depreciation_for_asset, etc.) the same as before
def get_accumulated_depreciation_for_asset(asset_name):
    """
    Calculate accumulated depreciation using available ERPNext functions
    """
    try:
        asset = frappe.get_doc("Asset", asset_name)
        accumulated_depreciation = 0
        num_booked = 0

        # Only calculate if depreciation is enabled
        if asset.calculate_depreciation and asset.gross_purchase_amount:
            try:
                # Get current asset value after depreciation
                current_asset_value = get_asset_value_after_depreciation(asset_name)
                accumulated_depreciation = asset.gross_purchase_amount - current_asset_value

                # Ensure accumulated depreciation doesn't exceed gross amount
                accumulated_depreciation = max(0, min(accumulated_depreciation, asset.gross_purchase_amount))

            except Exception as e:
                frappe.log_error(f"Error in get_asset_value_after_depreciation for {asset_name}: {str(e)}")
                # Fallback to direct calculation
                accumulated_depreciation = get_accumulated_depreciation_direct(asset_name)

        # Get count of booked depreciations
        num_booked = get_booked_depreciation_count(asset_name)

        frappe.logger().debug(f"Asset {asset_name}: Accumulated Depreciation = {accumulated_depreciation}, Booked Entries = {num_booked}")

        return accumulated_depreciation, num_booked

    except Exception as e:
        frappe.log_error(f"Error calculating depreciation for asset {asset_name}: {str(e)}")
        return 0, 0

def get_accumulated_depreciation_direct(asset_name):
    """Direct calculation of accumulated depreciation from GL entries"""
    try:
        query = """
            SELECT ABS(SUM(debit)) as accumulated_depreciation
            FROM `tabGL Entry`
            WHERE against_voucher = %s
            AND is_cancelled = 0
            AND docstatus = 1
            AND account in (
                SELECT depreciation_account
                FROM `tabAsset Category Account`
                WHERE parenttype = 'Asset Category'
            )
        """
        result = frappe.db.sql(query, asset_name, as_dict=True)
        return result[0].get('accumulated_depreciation', 0) if result else 0
    except Exception:
        return 0

def get_booked_depreciation_count(asset_name):
    """Get count of booked depreciation entries from depreciation schedule"""
    try:
        # First try: Count from Depreciation Entry table
        count = frappe.db.count("Depreciation Entry", {
            "asset_name": asset_name,
            "docstatus": 1
        })

        if count > 0:
            return count

        # Second try: Check depreciation schedule
        try:
            schedule = get_depr_schedule(asset_name, "Active")
            if schedule:
                # Count scheduled entries that have been posted
                booked_entries = [entry for entry in schedule if entry.get('journal_entry')]
                return len(booked_entries)
        except Exception as schedule_error:
            frappe.log_error(f"Error getting depreciation schedule: {str(schedule_error)}")

        # Final fallback: count from GL entries
        return count_depreciation_gl_entries(asset_name)

    except Exception as e:
        frappe.log_error(f"Error in get_booked_depreciation_count for {asset_name}: {str(e)}")
        return count_depreciation_gl_entries(asset_name)

def count_depreciation_gl_entries(asset_name):
    """Count depreciation entries from GL Entry"""
    try:
        query = """
            SELECT COUNT(DISTINCT voucher_no) as count
            FROM `tabGL Entry`
            WHERE against_voucher = %s
            AND is_cancelled = 0
            AND docstatus = 1
        """
        result = frappe.db.sql(query, asset_name, as_dict=True)
        return result[0].get('count', 0) if result else 0
    except Exception:
        return 0