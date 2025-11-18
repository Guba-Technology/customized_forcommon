import frappe
from frappe import _


def validate_account(doc, method):
    """Main validation hook for COA rules with numeric range enforcement."""

    # Get company
    company = doc.company or frappe.db.get_value("Account", doc.parent_account, "company")

    # Check if validation is enabled for this company
    enable_validation = frappe.db.get_value(
        "Company", company, "custom_enable_chart_of_accounts_validation"
    )

    if not enable_validation:
        return  # Skip all validations if not enabled

    # 1️⃣ Skip validation for root-level accounts
    if not doc.parent_account:
        # Still check root type consistency for top-level accounts
        validate_account_type_root_type(doc)
        return

    # 2️⃣ Check if the company uses 'Standard with Numbers'
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
    s = str(parent_num)
    trailing_zeros = len(s) - len(s.rstrip('0'))
    
    if trailing_zeros == 0:
        step = 1
    else:
        step = 10 ** trailing_zeros

    lower = parent_num
    upper = parent_num + step
    return lower, upper


# Mapping of Account Type → Root Type
ACCOUNT_ROOT_TYPE_MAP = {
    "Accumulated": "Depreciation Asset",
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
    "Round off for opening": ["Temporary", "Balance Sheet"],
    "Stock": "Asset",
    "Stock Adjustment": "Expense",
    "Stock Received but not billed": "Liability",
    "Service Received but not billed": "Liability",
    "Tax": "Liability",
    "Temporary": ["Temporary", "Balance Sheet"],
}


def validate_account_type_root_type(doc):
    """
    Enforce strict root_type validation with clear messages:
    1️⃣ Child must match parent root_type if parent exists
    2️⃣ Account type must be valid for root_type
    """

    # 1️⃣ Parent account validation
    if doc.parent_account:
        parent_root_type = frappe.db.get_value("Account", doc.parent_account, "root_type")
        if not parent_root_type:
            frappe.throw(_(
                f"Parent account '{doc.parent_account}' does not have a Root Type set. "
                "Please set it before adding child accounts."
            ))

        # Child root type must match parent
        if doc.root_type != parent_root_type:
            frappe.throw(_(
                f"Invalid Account Type '{doc.account_type}' for this parent account '{doc.parent_account}'. "
                f"The parent root type is '{parent_root_type}', so the child must have the same root type."
            ))

    # 2️⃣ Account type → root type validation (for top-level or standalone accounts)
    if not doc.account_type:
        return

    expected_root = ACCOUNT_ROOT_TYPE_MAP.get(doc.account_type)
    if not expected_root:
        return  # no mapping → skip

    # Multiple allowed root types (list)
    if isinstance(expected_root, list):
        if doc.root_type not in expected_root:
            frappe.throw(_(
                f"Invalid Account Type '{doc.account_type}' for Root Type '{doc.root_type}'. "
                f"Allowed Root Types: {', '.join(expected_root)}."
            ))
        return

    # Single expected root type
    if doc.root_type != expected_root:
        frappe.throw(_(
            f"Invalid Account Type '{doc.account_type}' for Root Type '{doc.root_type}'. "
            f"The Parent must be '{expected_root}'."
        ))
