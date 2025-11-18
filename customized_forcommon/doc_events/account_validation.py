import frappe
from frappe import _


def validate_account(doc, method):
    """Main validation hook for COA rules with numeric range enforcement."""

    # 1️⃣ Skip validation for root-level accounts
    if not doc.parent_account:
        # Still check root type consistency for top-level accounts
        validate_account_type_root_type(doc)
        return

    # 2️⃣ Check if the company uses 'Standard with Numbers'
    company = doc.company or frappe.db.get_value("Account", doc.parent_account, "company")
    coa_template = frappe.db.get_value("Company", company, "chart_of_accounts")
    if coa_template != "Standard with Numbers":
        # Still apply account-type to root-type validation
        validate_account_type_root_type(doc)
        return  # skip number-based validation for other templates

    # 3️⃣ Get parent account details
    parent_account = frappe.get_doc("Account", doc.parent_account)
    parent_number = parent_account.account_number

    if not parent_number:
        frappe.throw(_(
            f"Parent account '{parent_account.name}' has no account number defined. "
            "Please set one before adding child accounts."
        ))

    # 4️⃣ Validate child account number presence
    if not doc.account_number:
        frappe.throw(_("Please set an Account Number for this account."))

    # Ensure both are numeric
    try:
        parent_num = int(parent_number)
        child_num = int(doc.account_number)
    except ValueError:
        frappe.throw(_("Account numbers must be numeric for 'Standard with Numbers' COA."))

    # 5️⃣ Compute valid numeric range based on parent pattern
    lower_limit, upper_limit = get_allowed_range(parent_num)

    # 6️⃣ Validate child number range
    if not (lower_limit < child_num < upper_limit):
        frappe.throw(_(
            f"Invalid Account Number '{child_num}'. "
            f"It must be between {lower_limit + 1} and {upper_limit - 1} "
            f"based on parent account '{parent_number}'."
        ))

    # ✅ 7️⃣ Validate and auto-set root type consistency
    validate_account_type_root_type(doc)


def get_allowed_range(parent_num):
    """
    Determine allowed child number range based on trailing zeros in parent number.
    Example:
      1000 → (1000, 2000)
      1200 → (1200, 1300)
      1250 → (1250, 1260)
      100000 → (100000, 110000)
      500 → (500, 600)
    """
    s = str(parent_num)
    trailing_zeros = len(s) - len(s.rstrip('0'))
    
    if trailing_zeros == 0:
        # No trailing zeros → next 10 block
        step = 1
    else:
        step = 10 ** trailing_zeros

    lower = parent_num
    upper = parent_num + step
    return lower, upper


# -------------------------------------------------------------------
# ✅ NEW FUNCTION: Account Type ↔ Root Type validation and auto-setting
# -------------------------------------------------------------------

ACCOUNT_ROOT_TYPE_MAP = {
    "Accumulated Depreciation": "Asset",
    "Asset Received but not billed": "Liability",
    "Bank": "Asset",
    "Cash": "Asset",
    "Chargeable": ["Expense", "Income"],  # special case
    "Capital work in progress (CWIP)": "Asset",
    "Cost of goods sold (COGS)": "Expense",
    "Current Asset": "Asset",
    "Current Liability": "Liability",
    "Depreciation": "Expense",
    "Direct Expense": "Expense",
    "Direct Income": "Income",
    "Equity": "Equity",
    "Expense Account": "Expense",
    "Expense Included In Asset Valuation": "Expense",
    "Expense included in Valuation": "Expense",
    "Fixed Asset": "Asset",
    "Income Account": "Income",
    "Indirect Expense": "Expense",
    "Indirect Income": "Income",
    "Liability": "Liability",
    "Payable": "Liability",
    "Receivable": "Asset",
    "Round off": "Expense",
    "Round off for opening": ["Temporary", "Equity"],
    "Stock": "Asset",
    "Stock Adjustment": "Expense",
    "Stock Received but not billed": "Liability",
    "Service Received but not billed": "Liability",
    "Tax": "Liability",
    "Temporary": ["Temporary", "Equity"],
}


def validate_account_type_root_type(doc):
    """
    Validate and auto-set correct root_type based on account_type.
    Works for both group and individual accounts.
    """
    if not doc.account_type:
        return

    expected_root = ACCOUNT_ROOT_TYPE_MAP.get(doc.account_type)
    if not expected_root:
        return  # No mapping → skip

    # Multiple possible root types
    if isinstance(expected_root, list):
        if not doc.root_type:
            doc.root_type = expected_root[0]
            frappe.msgprint(_(
                f"Root Type automatically set to '{expected_root[0]}' "
                f"for Account Type '{doc.account_type}'."
            ))
        elif doc.root_type not in expected_root:
            frappe.throw(_(
                f"Invalid Root Type '{doc.root_type}' for Account Type '{doc.account_type}'. "
                f"Allowed: {', '.join(expected_root)}."
            ))
        return

    # Single expected root type
    if not doc.root_type:
        doc.root_type = expected_root
        frappe.msgprint(_(
            f"Root Type automatically set to '{expected_root}' "
            f"for Account Type '{doc.account_type}'."
        ))
    elif doc.root_type != expected_root:
        old_root = doc.root_type
        doc.root_type = expected_root
        frappe.msgprint(_(
            f"Root Type adjusted from '{old_root}' to '{expected_root}' "
            f"for Account Type '{doc.account_type}'."
        ))
