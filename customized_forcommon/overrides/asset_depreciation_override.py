# customized_forcommon/overrides/asset_depreciation_override.py

import frappe
from frappe.utils import flt, date_diff, getdate
from erpnext.assets.doctype.asset_depreciation_schedule.asset_depreciation_schedule import (
    AssetDepreciationSchedule,
    get_daily_prorata_based_straight_line_depr,
    get_asset_shift_factors_map,
    get_temp_asset_depr_schedule_doc
)
from erpnext.assets.doctype.asset.depreciation import (
    get_depreciation_accounts,
    get_disposal_account_and_cost_center
)

# -------------------------------
# Custom AssetDepreciationSchedule Class
# -------------------------------
class CustomAssetDepreciationSchedule(AssetDepreciationSchedule):
    def set_draft_asset_depr_schedule_details(self, asset_doc, row):
        """Override to use custom_cost_basis instead of gross_purchase_amount."""
        self.asset = asset_doc.name
        self.finance_book = row.finance_book
        self.finance_book_id = row.idx
        self.opening_accumulated_depreciation = asset_doc.opening_accumulated_depreciation or 0
        self.opening_number_of_booked_depreciations = asset_doc.opening_number_of_booked_depreciations or 0

        # USE CUSTOM COST BASIS
        self.gross_purchase_amount = getattr(row, "custom_cost_basis", None) or asset_doc.gross_purchase_amount

        self.depreciation_method = row.depreciation_method
        self.total_number_of_depreciations = row.total_number_of_depreciations
        self.frequency_of_depreciation = row.frequency_of_depreciation
        self.rate_of_depreciation = row.rate_of_depreciation
        self.expected_value_after_useful_life = row.expected_value_after_useful_life
        self.daily_prorata_based = row.daily_prorata_based
        self.shift_based = row.shift_based
        self.status = "Draft"


# -------------------------------
# Module-level function overrides
# -------------------------------

def custom_get_value_after_depreciation_for_making_schedule(asset_doc, fb_row):
    """Use custom_cost_basis if available."""
    if asset_doc.docstatus == 1 and getattr(fb_row, "value_after_depreciation", None):
        return flt(fb_row.value_after_depreciation)

    custom_cost_basis = getattr(fb_row, "custom_cost_basis", None) or asset_doc.gross_purchase_amount
    return flt(custom_cost_basis) - flt(asset_doc.opening_accumulated_depreciation)


def custom_get_shift_depr_amount(asset_depr_schedule, asset, row, schedule_idx):
    """Shift-based depreciation using custom_cost_basis."""
    if asset_depr_schedule.get("__islocal") and not getattr(asset.flags, "shift_allocation", False):
        custom_cost_basis = getattr(row, "custom_cost_basis", None) or asset.gross_purchase_amount
        return (
            flt(custom_cost_basis)
            - flt(asset.opening_accumulated_depreciation)
            - flt(row.expected_value_after_useful_life)
        ) / flt(row.total_number_of_depreciations - asset.opening_number_of_booked_depreciations)

    asset_shift_factors_map = get_asset_shift_factors_map()
    shift = (
        asset_depr_schedule.schedules_before_clearing[schedule_idx].shift
        if len(asset_depr_schedule.schedules_before_clearing) > schedule_idx
        else None
    )
    shift_factor = asset_shift_factors_map.get(shift) if shift else 0

    shift_factors_sum = sum(
        flt(asset_shift_factors_map.get(schedule.shift))
        for schedule in asset_depr_schedule.schedules_before_clearing
    )

    custom_cost_basis = getattr(row, "custom_cost_basis", None) or asset.gross_purchase_amount
    return (
        (flt(custom_cost_basis) - flt(asset.opening_accumulated_depreciation) - flt(row.expected_value_after_useful_life))
        / flt(shift_factors_sum)
    ) * shift_factor


def custom_get_straight_line_or_manual_depr_amount(asset_depr_schedule, asset, row, schedule_idx, number_of_pending_depreciations):
    """Straight-line/manual depreciation using custom_cost_basis."""
    if row.shift_based:
        return custom_get_shift_depr_amount(asset_depr_schedule, asset, row, schedule_idx)

    custom_cost_basis = getattr(row, "custom_cost_basis", None) or asset.gross_purchase_amount

    if getattr(asset.flags, "increase_in_asset_life", False):
        return (flt(row.value_after_depreciation) - flt(row.expected_value_after_useful_life)) / (
            date_diff(asset.to_date, asset.available_for_use_date) / 365
        )
    elif getattr(asset.flags, "increase_in_asset_value_due_to_repair", False):
        return (flt(row.value_after_depreciation) - flt(row.expected_value_after_useful_life)) / flt(number_of_pending_depreciations)
    elif getattr(asset.flags, "decrease_in_asset_value_due_to_value_adjustment", False):
        if row.daily_prorata_based:
            amount = flt(row.value_after_depreciation) - flt(row.expected_value_after_useful_life)
            return get_daily_prorata_based_straight_line_depr(asset, row, schedule_idx, number_of_pending_depreciations, amount)
        else:
            return (flt(row.value_after_depreciation) - flt(row.expected_value_after_useful_life)) / number_of_pending_depreciations
    else:
        # First-time depreciation
        if row.daily_prorata_based:
            amount = flt(custom_cost_basis) - flt(row.expected_value_after_useful_life)
            return get_daily_prorata_based_straight_line_depr(asset, row, schedule_idx, number_of_pending_depreciations, amount)
        else:
            return (flt(custom_cost_basis) - flt(row.expected_value_after_useful_life)) / flt(row.total_number_of_depreciations)


def custom_get_asset_details(asset, finance_book=None):
    """Use custom_cost_basis to calculate accumulated depreciation."""
    value_after_depreciation = asset.get_value_after_depreciation(finance_book)
    fb_row = None

    if finance_book:
        for row in asset.get("finance_books"):
            if row.finance_book == finance_book:
                fb_row = row
                break

    gross_purchase_amount = getattr(fb_row, "custom_cost_basis", None) if fb_row else asset.gross_purchase_amount
    accumulated_depr_amount = flt(gross_purchase_amount) - flt(value_after_depreciation)

    fixed_asset_account, accumulated_depr_account, _ = get_depreciation_accounts(asset.asset_category, asset.company)
    disposal_account, depreciation_cost_center = get_disposal_account_and_cost_center(asset.company)
    depreciation_cost_center = asset.cost_center or depreciation_cost_center

    return (
        fixed_asset_account,
        asset,
        depreciation_cost_center,
        accumulated_depr_account,
        accumulated_depr_amount,
        disposal_account,
        value_after_depreciation,
    )


def custom_get_value_after_depreciation_on_disposal_date(asset, disposal_date, finance_book=None):
    """Use custom_cost_basis for disposal calculation."""
    asset_doc = frappe.get_doc("Asset", asset)

    if asset_doc.available_for_use_date > getdate(disposal_date):
        frappe.throw(
            f"Disposal date {disposal_date} cannot be before available for use date {asset_doc.available_for_use_date} of the asset."
        )
    elif asset_doc.available_for_use_date == getdate(disposal_date):
        custom_cost_basis = None
        if finance_book:
            for row in asset_doc.finance_books:
                if row.finance_book == finance_book and getattr(row, "custom_cost_basis", None):
                    custom_cost_basis = row.custom_cost_basis
                    break
        gross_purchase_amount = custom_cost_basis or asset_doc.gross_purchase_amount
        return flt(gross_purchase_amount - asset_doc.opening_accumulated_depreciation)

    if not asset_doc.calculate_depreciation:
        return flt(asset_doc.value_after_depreciation)

    idx = 1
    if finance_book:
        for d in asset_doc.finance_books:
            if d.finance_book == finance_book:
                idx = d.idx
                if getattr(d, "custom_cost_basis", None):
                    asset_doc.gross_purchase_amount = d.custom_cost_basis
                break

    row = asset_doc.finance_books[idx - 1]
    temp_asset_depreciation_schedule = get_temp_asset_depr_schedule_doc(asset_doc, row, getdate(disposal_date))
    accumulated_depr_amount = temp_asset_depreciation_schedule.get("depreciation_schedule")[-1].accumulated_depreciation_amount
    gross_purchase_amount = getattr(row, "custom_cost_basis", None) or asset_doc.gross_purchase_amount

    return flt(flt(gross_purchase_amount) - accumulated_depr_amount, asset_doc.precision("gross_purchase_amount"))

# -------------------------------
# Apply module-level monkey patches
# -------------------------------
def apply_patches():
    import erpnext.assets.doctype.asset_depreciation_schedule.asset_depreciation_schedule as ads

    ads.get_straight_line_or_manual_depr_amount = custom_get_straight_line_or_manual_depr_amount
    ads.get_shift_depr_amount = custom_get_shift_depr_amount
    ads.get_value_after_depreciation_for_making_schedule = custom_get_value_after_depreciation_for_making_schedule
    ads.get_asset_details = custom_get_asset_details
    ads.get_value_after_depreciation_on_disposal_date = custom_get_value_after_depreciation_on_disposal_date
