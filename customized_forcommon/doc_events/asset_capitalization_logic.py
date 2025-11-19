import frappe
from frappe import _
from erpnext.assets.doctype.asset.asset import get_asset_value_after_depreciation, get_depr_schedule

def update_child_table_after_capitalization(doc, method):
    try:
        if doc.doctype != "Asset Capitalization":
            return

        if not doc.asset_items:
            return

        for asset_item in doc.asset_items:
            asset_name = asset_item.asset

            accumulated_amount, num_booked = get_accumulated_depreciation_for_asset(asset_name)
            depreciation_start_date = get_depreciation_start_date(frappe.get_doc("Asset", asset_name))

            # Get the cost from Asset Capitalization (use total_value)
            cost_amount = doc.total_value or 0

            # Insert child table row with cost field
            frappe.db.sql("""
                INSERT INTO `tabAsset Capitalization Detail`
                (name, parent, parentfield, parenttype, idx, date_of_capitalization, depreciation_start_date, opening_accumulated_d, opening_number_o, cost)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                frappe.generate_hash("", 10),
                asset_name,
                "capitalization_details",
                "Asset",
                0,  # idx
                doc.posting_date or frappe.utils.nowdate(),
                depreciation_start_date,
                accumulated_amount,
                num_booked,
                cost_amount  # Add the cost field
            ))

        frappe.db.commit()

    except Exception as e:
        short_error = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
        frappe.log_error(f"Asset Cap Error: {short_error}")
        frappe.throw(_("Update failed: {0}").format(short_error))

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
        custom_accumulated = getattr(doc, 'opening_accumulated', 0) or 0
        parent_opening_number = getattr(doc, 'opening_number', 0) or 0

        total_opening_number_o = 0
        if hasattr(doc, 'capitalization_details') and doc.capitalization_details:
            for row in doc.capitalization_details:
                total_opening_number_o += (row.opening_number_o or 0)

        # 3️⃣ Sum them and set into ERPNext built-in system field
        doc.opening_number_of_booked_depreciations = parent_opening_number + total_opening_number_o


        # Sync custom fields with built-in fields
        # Set first_purchase_amount from gross_purchase_amount (only if empty)
        if not getattr(doc, 'first_purchase_amount', None) and doc.gross_purchase_amount:
            doc.first_purchase_amount = doc.gross_purchase_amount

        # Calculate sum of all cost fields in child table
        total_child_costs = 0
        # Calculate sum of all opening_accumulated_d fields in child table
        total_opening_accumulated_d = 0

        if hasattr(doc, 'capitalization_details') and doc.capitalization_details:
            for row in doc.capitalization_details:
                total_child_costs += (row.cost or 0)
                total_opening_accumulated_d += (row.opening_accumulated_d or 0)

        doc.opening_accumulated_depreciation = custom_accumulated + total_opening_accumulated_d

        # Get first_purchase_amount (use current value or default to 0)
        first_purchase_amount = getattr(doc, 'first_purchase_amount', 0) or 0

        # Calculate total accumulated depreciation (main asset field + sum from child table)
        total_accumulated_depreciation = custom_accumulated + total_opening_accumulated_d

        # Store old value for comparison (FIXED: define old_gross_amount)
        old_gross_amount = doc.gross_purchase_amount

        # Set gross_purchase_amount to the sum
        doc.gross_purchase_amount = first_purchase_amount + total_child_costs
    except Exception as e:
        error_msg = f"❌ Error in sync_custom_fields: {str(e)}"
        frappe.msgprint(error_msg)
        frappe.log_error(f"Error in sync_custom_fields: {str(e)}")

# Keep the other functions the same...
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

def get_depreciation_start_date(asset):
    """Get depreciation start date from asset"""
    try:
        # Try to get from finance books first
        if asset.finance_books and len(asset.finance_books) > 0:
            return asset.finance_books[0].depreciation_start_date

        # Fallback to available_for_use_date
        return asset.available_for_use_date or asset.purchase_date

    except Exception:
        # Final fallback
        return asset.available_for_use_date or asset.purchase_date or frappe.utils.nowdate()

def set_default_values(doc,method):
    """Set default values BEFORE mandatory field validation."""
    if not doc.gross_purchase_amount or doc.gross_purchase_amount == 0:
        doc.gross_purchase_amount = doc.first_purchase_amount or 1
    cap_rows = doc.get("capitalization_details") or []
    if cap_rows:
        last_row = cap_rows[-1]

        # Use capitalization row values (if available)
        if last_row.get("date_of_capitalization"):
            doc.purchase_date = last_row.date_of_capitalization

        if last_row.get("depreciation_start_date"):
            doc.available_for_use_date = last_row.depreciation_start_date

    else:
        # 3️⃣ Fallback logic when no child table rows exist
        if not doc.purchase_date:
            doc.purchase_date = frappe.utils.nowdate()

        if not doc.available_for_use_date:
            doc.available_for_use_date = doc.purchase_date