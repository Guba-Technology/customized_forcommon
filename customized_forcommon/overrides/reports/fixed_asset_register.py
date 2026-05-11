# Only fix prepare_chart_data to avoid KeyError
from collections import OrderedDict
import frappe
from frappe.utils import formatdate, flt

def prepare_chart_data(data, filters):
    """
    Safe version of prepare_chart_data for Fixed Asset Register
    """
    if not data:
        return

    labels_values_map = OrderedDict()

    # Determine date field
    date_field = frappe.scrub(filters.get("date_based_on") or "purchase_date")

    # First pass: collect months dynamically
    for d in data:
        if d.get(date_field):
            belongs_to_month = formatdate(d.get(date_field), "MMM YYYY")
            if belongs_to_month not in labels_values_map:
                labels_values_map[belongs_to_month] = frappe._dict({
                    "asset_value": 0,
                    "depreciated_amount": 0
                })

    # Second pass: aggregate values safely
    for d in data:
        if d.get(date_field):
            belongs_to_month = formatdate(d.get(date_field), "MMM YYYY")
            labels_values_map[belongs_to_month].asset_value += flt(d.get("asset_value"))
            labels_values_map[belongs_to_month].depreciated_amount += flt(d.get("depreciated_amount"))

    # Build chart
    return {
        "data": {
            "labels": list(labels_values_map.keys()),
            "datasets": [
                {
                    "name": "Asset Value",
                    "values": [flt(v.asset_value, 2) for v in labels_values_map.values()],
                },
                {
                    "name": "Depreciated Amount",
                    "values": [flt(v.depreciated_amount, 2) for v in labels_values_map.values()],
                },
            ],
        },
        "type": "bar",
        "barOptions": {"stacked": 1},
    }