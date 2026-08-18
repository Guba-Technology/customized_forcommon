import frappe
from frappe import _
from frappe.utils import flt, getdate


def process_profit_tax_provision(doc, method=None):
    """
    Hooked on validate or before_submit of Period Closing Voucher / Fiscal Year Closing.
    Calculates taxable profit and posts profit tax provision Journal Entry.
    """
    # 1. Check if feature is enabled in Accounting Settings
    enable_tax = frappe.db.get_single_value("Accounts Settings", "custom_enable_automatic_profit_tax_posting_during_fiscal_closing")
    if not enable_tax:
        return

    company = doc.company
    posting_date = doc.transaction_date

    # 2. Fetch Company Tax Configuration
    company_doc = frappe.get_doc("Company", company)
    tax_rate = flt(company_doc.get("custom_profit_tax_rate"))
    expense_account = company_doc.get("custom_profit_tax_expense_account")
    provision_account = company_doc.get("custom_profit_tax_provision_account")

    if not tax_rate or tax_rate <= 0:
        frappe.throw(_("Please configure a valid Profit Tax Rate (%) in Company: {0}").format(company))
    if not expense_account or not provision_account:
        frappe.throw(_("Please configure Profit Tax Expense and Provision Accounts in Company: {0}").format(company))

    # 3. Calculate Taxable Income and Expense
    taxable_income = get_account_type_balance(
        company=company,
        root_type="Income",
        from_date=doc.period_start_date,
        to_date=doc.period_end_date
    )

    taxable_expense = get_account_type_balance(
        company=company,
        root_type="Expense",
        from_date=doc.period_start_date,
        to_date=doc.period_end_date
    )

    # Taxable Profit = Taxable Income - Taxable Expenses
    taxable_profit = flt(taxable_income) - flt(taxable_expense)

    if taxable_profit <= 0:
        frappe.msgprint(_("Taxable profit is zero or negative ({0}). No profit tax provision posted.").format(taxable_profit))
        return

    # 4. Calculate Profit Tax
    tax_amount = flt(taxable_profit * (tax_rate / 100.0), doc.precision("grand_total"))

    if tax_amount <= 0:
        return

    # 5. Create and Submit Journal Entry
    make_profit_tax_journal_entry(
        company=company,
        posting_date=posting_date,
        expense_account=expense_account,
        provision_account=provision_account,
        tax_amount=tax_amount,
        user_remark=f"Profit Tax Provision for Fiscal Year {doc.fiscal_year} (Taxable Profit: {taxable_profit})"
    )


def get_account_type_balance(company, root_type, from_date, to_date):
    """
    Sum GL Entries for Income or Expense accounts where `is_not_taxable` is 0/Unchecked.
    """
    gl_entries = frappe.db.sql("""
        SELECT 
            SUM(gle.credit - gle.debit) as net_credit,
            SUM(gle.debit - gle.credit) as net_debit
        FROM `tabGL Entry` gle
        INNER JOIN `tabAccount` acc ON gle.account = acc.name
        WHERE 
            gle.company = %s
            AND gle.posting_date BETWEEN %s AND %s
            AND acc.root_type = %s
            AND IFNULL(acc.custom_is_not_taxable, 0) = 0
            AND gle.is_cancelled = 0
    """, (company, from_date, to_date, root_type), as_dict=True)

    if not gl_entries:
        return 0.0

    # Income is credit-based; Expense is debit-based
    if root_type == "Income":
        return flt(gl_entries[0].net_credit)
    else:
        return flt(gl_entries[0].net_debit)


def make_profit_tax_journal_entry(company, posting_date, expense_account, provision_account, tax_amount, user_remark):
    """
    Posts the Profit Tax Journal Entry prior to period closing execution.
    """
    je = frappe.new_doc("Journal Entry")
    je.voucher_type = "Journal Entry"
    je.company = company
    je.posting_date = posting_date
    je.user_remark = user_remark

    # Debit Expense Account
    je.append("accounts", {
        "account": expense_account,
        "debit_in_account_currency": tax_amount,
        "credit_in_account_currency": 0,
        "user_remark": "Profit Tax Provision Expense"
    })

    # Credit Provision Account
    je.append("accounts", {
        "account": provision_account,
        "debit_in_account_currency": 0,
        "credit_in_account_currency": tax_amount,
        "user_remark": "Profit Tax Payable/Provision"
    })

    je.insert(ignore_permissions=True)
    je.submit()
    
    frappe.msgprint(_("Created and submitted Profit Tax Provision Journal Entry: {0}").format(je.name))