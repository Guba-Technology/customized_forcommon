import frappe
from erpnext.accounts.report.general_ledger.general_ledger import execute as gl_execute

def execute(filters=None):
    # Ensure 'account' filter is always a list
    if filters and filters.get("account") and isinstance(filters.get("account"), str):
        filters["account"] = [filters["account"]]

    # Use built-in General Ledger logic (keeps balances perfect)
    columns, data = gl_execute(filters)

    # Ensure 'party' and 'party_type' always exist
    for row in data:
        row.setdefault("party", "")
        row.setdefault("party_type", "")

    # Move 'party' column after 'party_type'
    def move_column_after(columns, fieldname_to_move, reference_fieldname):
        ref_index = next((i for i, col in enumerate(columns) if col.get("fieldname") == reference_fieldname), None)
        if ref_index is not None:
            for i, col in enumerate(columns):
                if col.get("fieldname") == fieldname_to_move:
                    columns.insert(ref_index + 1, columns.pop(i))
                    break

    move_column_after(columns, "party", "party_type")

    return columns, data
