import frappe
from frappe import _
from frappe.utils import flt, getdate
from erpnext.accounts.utils import get_balance_on


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()

    if not filters.get("account"):
        return columns, []

    account_currency = frappe.get_cached_value("Account", filters.account, "account_currency")
    data = get_entries(filters)

    # Balance as per system
    balance_as_per_system = get_balance_on(filters["account"], filters["report_date"])

    # Total outstanding cheques/deposits
    total_debit, total_credit = 0, 0
    for d in data:
        total_debit += flt(d["debit"])
        total_credit += flt(d["credit"])

    # Amounts not reflected in system
    amounts_not_reflected_in_system = get_amounts_not_reflected_in_system(filters)

    # -------------------------
    # In-Transit Entries & Totals
    # -------------------------
    deposit_entries, deposit_total = get_in_transit_entries(filters, "custom_deposit_in_transit")
    withdraw_entries, withdraw_total = get_in_transit_entries(filters, "custom_withdrawals_in_transit")

    # Final calculated bank balance
    bank_bal = (
        flt(balance_as_per_system)
        - flt(total_debit)
        + flt(total_credit)
        + amounts_not_reflected_in_system
        + deposit_total
        - withdraw_total
    )

    # Build report data
    data += [
        get_balance_row(_("Bank Statement balance as per General Ledger"), balance_as_per_system, account_currency),
        {},
        {
            "payment_entry": _("Outstanding Cheques and Deposits to clear"),
            "debit": total_debit,
            "credit": total_credit,
            "account_currency": account_currency,
        },
        get_balance_row(_("Cheques and Deposits incorrectly cleared"), amounts_not_reflected_in_system, account_currency),
        {},
        # Append all deposit in-transit transactions
        *deposit_entries,
        {"payment_entry": _("Deposits in Transit Entries"), "debit": deposit_total, "credit": 0, "account_currency": account_currency},
        # Append all withdrawal in-transit transactions
        *withdraw_entries,
        {"payment_entry": _("Withdrawals in Transit Entries"), "debit": 0, "credit": withdraw_total, "account_currency": account_currency},
        {},
        get_balance_row(_("Calculated Bank Statement balance"), bank_bal, account_currency),
    ]

    return columns, data


# -------------------------
# Helper Functions
# -------------------------

def get_columns():
    return [
        {"fieldname": "posting_date", "label": _("Posting Date"), "fieldtype": "Date", "width": 90},
        {"fieldname": "payment_document", "label": _("Payment Document Type"), "fieldtype": "Data", "width": 220},
        {
            "fieldname": "payment_entry",
            "label": _("Payment Document"),
            "fieldtype": "Dynamic Link",
            "options": "payment_document",
            "width": 220,
        },
        {"fieldname": "debit", "label": _("Debit"), "fieldtype": "Currency", "options": "account_currency", "width": 120},
        {"fieldname": "credit", "label": _("Credit"), "fieldtype": "Currency", "options": "account_currency", "width": 120},
        {"fieldname": "against_account", "label": _("Against Account"), "fieldtype": "Link", "options": "Account", "width": 200},
        {"fieldname": "reference_no", "label": _("Reference"), "fieldtype": "Data", "width": 100},
        {"fieldname": "ref_date", "label": _("Ref Date"), "fieldtype": "Date", "width": 110},
        {"fieldname": "clearance_date", "label": _("Clearance Date"), "fieldtype": "Date", "width": 110},
        {"fieldname": "account_currency", "label": _("Currency"), "fieldtype": "Link", "options": "Currency", "width": 100},
    ]


def get_entries(filters):
    entries = []
    for method_name in frappe.get_hooks("get_entries_for_bank_reconciliation_statement"):
        entries += frappe.get_attr(method_name)(filters) or []
    return sorted(entries, key=lambda k: getdate(k["posting_date"]))


def get_amounts_not_reflected_in_system(filters):
    amount = 0.0
    for method_name in frappe.get_hooks("get_amounts_not_reflected_in_system_for_bank_reconciliation_statement"):
        amount += frappe.get_attr(method_name)(filters) or 0.0
    return amount


def get_in_transit_entries(filters, account_field):
    """
    Fetch all transactions posted to in-transit accounts (Journal Entry + Payment Entry)
    Returns both the list of entries and total (debit or credit depending on type)
    """
    company = filters.get("company")
    bank_account = filters.get("account")
    transit_account = frappe.get_cached_value("Company", company, account_field)
    if not transit_account:
        return [], 0.0

    report_date = filters.get("report_date")
    entries = []

    # -------------------------
    # Journal Entry transactions
    # -------------------------
    je_entries = frappe.db.sql(
        """
        SELECT
            jv.posting_date, "Journal Entry" as payment_document, jvd.parent as payment_entry,
            jvd.debit_in_account_currency as debit, jvd.credit_in_account_currency as credit,
            jvd.against_account, jv.cheque_no as reference_no, jv.cheque_date as ref_date, jv.clearance_date
        FROM `tabJournal Entry Account` jvd
        JOIN `tabJournal Entry` jv ON jvd.parent = jv.name
        WHERE jvd.account=%(transit_account)s
          AND jv.docstatus=1
          AND jv.posting_date <= %(report_date)s
          AND jv.company=%(company)s
          AND jvd.against_account=%(bank_account)s
        """,
        {
            "transit_account": transit_account,
            "report_date": report_date,
            "company": company,
            "bank_account": bank_account,
        },
        as_dict=True,
    )
    entries += je_entries

    # -------------------------
    # Payment Entry transactions
    # -------------------------
    pe_entries = frappe.db.sql(
        """
        SELECT
            posting_date, "Payment Entry" as payment_document, name as payment_entry,
            IF(paid_to=%(transit_account)s, received_amount_after_tax, 0) as debit,
            IF(paid_from=%(transit_account)s, paid_amount_after_tax, 0) as credit,
            IFNULL(party,IF(paid_from=%(transit_account)s,paid_to,paid_from)) as against_account,
            reference_no, reference_date as ref_date, clearance_date
        FROM `tabPayment Entry`
        WHERE (paid_from=%(transit_account)s OR paid_to=%(transit_account)s)
          AND docstatus=1
          AND posting_date <= %(report_date)s
          AND company=%(company)s
          AND (paid_to=%(bank_account)s OR paid_from=%(bank_account)s)
        """,
        {
            "transit_account": transit_account,
            "report_date": report_date,
            "company": company,
            "bank_account": bank_account,
        },
        as_dict=True,
    )
    entries += pe_entries

    # -------------------------
    # Calculate totals
    # -------------------------
    total_debit = sum(flt(d["debit"]) for d in entries)
    total_credit = sum(flt(d["credit"]) for d in entries)

    if account_field == "custom_deposit_in_transit":
    # Deposits: transit account is credited (money coming in to bank)
        total = total_credit
    else:
        # Withdrawals: transit account is debited (money leaving the bank)
        total = total_debit

    return entries, total


def get_balance_row(label, amount, account_currency):
    if amount > 0:
        return {"payment_entry": label, "debit": amount, "credit": 0, "account_currency": account_currency}
    else:
        return {"payment_entry": label, "debit": 0, "credit": abs(amount), "account_currency": account_currency}
