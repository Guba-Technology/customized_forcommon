from erpnext.accounts.general_ledger import make_gl_entries
from frappe.utils.nestedset import get_descendants_of
import frappe
from frappe import _
from frappe.utils import today, flt, getdate, date_diff, now_datetime

# updating the status of the purchase invoice 
@frappe.whitelist()
def update_invoice_status(docname, new_status):
    try:
        doc = frappe.get_doc("Purchase Invoice", docname)
        doc.db_set("status", new_status)  # Force update status
        frappe.db.commit()
        return "success"
    except Exception as e:
        frappe.log_error(f"Error updating status: {str(e)}", "Purchase Invoice Status Update")
        return "error"

# This function retrieves the first item from a Material Request and returns its item code.
@frappe.whitelist()
def get_item_for_bom(material_request):
    doc = frappe.get_doc("Material Request", material_request)
    if doc.items and len(doc.items) > 0:
        message = ""
        if len(doc.items) > 1:
            message = f"There are {len(doc.items)} items in the Material Request. BOM will be created only for the first item."
        return {
            "item_code": doc.items[0].item_code,
            "message": message
        }
    return None

@frappe.whitelist()
def purchase_invoice_id(purchase_invoice):
    doc = frappe.get_doc("Purchase Invoice", purchase_invoice)
    return {"purchase_invoice_id": doc.name}
    

# This function retrieves the quantity of a specific item in a given reference document (Purchase Receipt or Purchase Invoice).
@frappe.whitelist()
def get_reference_item_qty(reference_type, reference_name, item_code):
    if not frappe.has_permission(reference_type, "read"):
        frappe.throw(_("Not permitted"))

    # Handle child table-based references
    child_doctype = None

    if reference_type == "Purchase Receipt":
        child_doctype = "Purchase Receipt Item"
    elif reference_type == "Purchase Invoice":
        child_doctype = "Purchase Invoice Item"
    elif reference_type == "Delivery Note":
        child_doctype = "Delivery Note Item"
    elif reference_type == "Sales Invoice":
        child_doctype = "Sales Invoice Item"
    elif reference_type == "Stock Entry":
        child_doctype = "Stock Entry Detail"
    elif reference_type == "Job Card":
        # Job Card is a parent DocType, get total_completed_qty directly
        return frappe.db.get_value("Job Card", reference_name, "total_completed_qty") or 0
    else:
        frappe.throw(_("Unsupported Reference Type: {0}").format(reference_type))

    # Fallback for child Doctypes
    qty = frappe.db.get_value(
        child_doctype,
        {"parent": reference_name, "item_code": item_code},
        "qty"
    )
    return qty or 0


# This function retrieves all users, including disabled and unsaved ones, for the User Company Assignment form.
@frappe.whitelist()
def get_available_users_for_assignment(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""
        SELECT 
            u.name, 
            CONCAT(u.first_name, ' ', IFNULL(u.last_name, ''), IF(u.enabled = 0, ' (Disabled)', '')) AS full_name
        FROM `tabUser` u
        WHERE (
            u.name = 'Administrator' OR u.name NOT IN (
                SELECT user FROM `tabUser Company Assignment`
            )
        )
        AND (u.name LIKE %(txt)s 
            OR u.first_name LIKE %(txt)s 
            OR u.last_name LIKE %(txt)s)
        ORDER BY u.creation DESC
        LIMIT %(start)s, %(page_len)s
    """, {
        "txt": f"%{txt}%",
        "start": start,
        "page_len": page_len
    })

# This function retrieves the count of employees and job openings for a given designation, company, and optional department.
@frappe.whitelist()
def get_designation_counts(designation, company, department=None):
    if not designation:
        return {"employee_count": 0, "job_openings": 0}

    company_set = get_descendants_of("Company", company)
    company_set.append(company)

    employee_filters = {
        "designation": designation,
        "status": "Active",
        "company": ("in", company_set),
    }

    if department:
        employee_filters["department"] = department

    employee_count = frappe.db.count("Employee", employee_filters)

    job_filters = {
        "designation": designation,
        "status": "Open",
        "company": ("in", company_set),
    }

    if department:
        job_filters["department"] = department

    job_openings = frappe.db.count("Job Opening", job_filters)

    return {
        "employee_count": employee_count,
        "job_openings": job_openings
    }

@frappe.whitelist()
def get_data_from_purchase_order(purchase_order_doc):
    purchase_order = frappe.get_doc("Purchase Order", purchase_order_doc)
    employee = purchase_order.custom_employee
    date = purchase_order.transaction_date
    company = purchase_order.company

    return {"employee": employee, "date": date, "company": company}


@frappe.whitelist()
def get_item_tax_accounts(item_code, company=None, net_amount=0, posting_date=None):
    """
    Get tax accounts and rates for an Item via Item Tax Templates,
    filtered by company and respecting Item-level conditions:
    - valid_from
    - minimum_net_rate
    - maximum_net_rate
    """
    if not posting_date:
        posting_date = today()

    item = frappe.get_doc("Item", item_code)
    tax_accounts = []

    for item_tax in item.get("taxes") or []:
        if not item_tax.item_tax_template:
            continue

        template = frappe.get_doc("Item Tax Template", item_tax.item_tax_template)

        # Convert min/max net rates to float safely
        min_rate = flt(item_tax.minimum_net_rate)
        max_rate = flt(item_tax.maximum_net_rate)
        net_amount = flt(net_amount)


        # Check Item-level conditions
        if getdate(item_tax.valid_from) and getdate(posting_date) < getdate(item_tax.valid_from):
            continue
        if min_rate and net_amount < min_rate:
            continue
        if max_rate and net_amount > max_rate:
            continue

        for tax_row in template.taxes:
            account = tax_row.tax_type
            account_doc = frappe.get_doc("Account", account)

            # Skip accounts that do not belong to the company
            if company and account_doc.company != company:
                continue

            tax_accounts.append({
                "template": template.name,
                "account": account,
                "account_name": account_doc.account_name,
                "rate": tax_row.tax_rate
            })

    return tax_accounts

def calculate_employee_severance_amount(doc, hr_settings): # accept hr_settings to sync the current values
    from dateutil.relativedelta import relativedelta

    if not doc.relieving_date or not doc.date_of_joining or not doc.custom_apply_severance_pay:
        return 0

    starting_year = hr_settings.custom_severenace_pay_starting_year or 1
    first_year_severance_days = hr_settings.custom_first_year_severance_days or 0
    subsequent_year_severance_days = hr_settings.custom_subsequent_year_severance_days or 0
    salary_divisor_days = hr_settings.custom_salary_divisor_days or 0

    basic_salary = doc.ctc or 0

    if basic_salary <= 0:
        return 0

    if salary_divisor_days > 0:
        daily_wage = basic_salary / salary_divisor_days
    else:
        daily_wage = 0

    service = relativedelta(getdate(doc.relieving_date), getdate(doc.date_of_joining))

    full_years = service.years
    full_months = service.months
    remaining_days = service.days

    # Not Eligible
    if full_years < starting_year:
        return 0
    
    if full_years <= 1:
        severance = daily_wage * first_year_severance_days
    else:
        severance = (daily_wage * first_year_severance_days) + ((full_years - 1) * subsequent_year_severance_days * daily_wage)

        # Remaining Months and Days
        remaining_year_fraction = ((full_months / 12) + (remaining_days / 365))
        severance += (remaining_year_fraction * subsequent_year_severance_days * daily_wage)

    return severance

# As of Today Leave Balance (Fiscal Year Based)
@frappe.whitelist()
def calculate_as_of_today_balance(employee, leave_type):
    today = getdate()

    # -----------------------------
    # 1. Get Fiscal Year
    # -----------------------------
    fy = frappe.db.sql("""
        SELECT name, year_start_date, year_end_date
        FROM `tabFiscal Year`
        WHERE %s BETWEEN year_start_date AND year_end_date
        LIMIT 1
    """, (today,), as_dict=True)

    if not fy:
        return 0

    fy = fy[0]

    # -----------------------------
    # 2. Check Leave Type
    # -----------------------------
    leave_type_doc = frappe.get_doc("Leave Type", leave_type)

    if not leave_type_doc.is_carry_forward:
        return 0

    # -----------------------------
    # 3. Get Annual Allocation
    # -----------------------------
    allocation = frappe.db.get_value(
        "Leave Allocation",
        {
            "employee": employee,
            "leave_type": leave_type,
            "docstatus": 1
        },
        "total_leaves_allocated"
    ) or 0

    # -----------------------------
    # 4. Total Used Leave
    # -----------------------------
    used = frappe.db.sql("""
        SELECT COALESCE(SUM(total_leave_days), 0)
        FROM `tabLeave Application`
        WHERE employee = %s
            AND leave_type = %s
            AND status = 'Approved'
            AND docstatus = 1
            AND from_date <= %s
    """, (employee, leave_type, today))[0][0]

    # -----------------------------
    # 5. Fiscal Month Index (based on FY start date)
    # -----------------------------
    start = fy.year_start_date

    fiscal_month = ((today.year - start.year) * 12 +
                    (today.month - start.month)) + 1

    # clamp between 1 and 12
    fiscal_month = max(1, min(fiscal_month, 12))

    # -----------------------------
    # 6. Simple Monthly Accrual Logic
    # -----------------------------
    earned = (allocation / 12.0) * fiscal_month
    balance = earned - used

    return round(balance, 2)




@frappe.whitelist()
def get_lc_invoice_and_payment_entry_costs(
    receipt_document_type,
    receipt_document
):

    if receipt_document_type != "Purchase Receipt":
        return []


    pr = frappe.get_doc(
        "Purchase Receipt",
        receipt_document
    )


    if not pr.custom_purchase_order:
        return []


    po = frappe.get_doc(
        "Purchase Order",
        pr.custom_purchase_order
    )


    if not po.custom_lc_number:
        return []


    lc = frappe.get_doc(
        "LC Master",
        po.custom_lc_number
    )


    taxes = []
    processed_invoices = set()
    processed_payments = set()
    processed_journal_entries = set()


    # Purchase Invoice Costs
    for invoice_row in lc.linked_purchase_invoices:

        if invoice_row.purchase_invoice in processed_invoices:
            continue


        pi = frappe.get_doc(
            "Purchase Invoice",
            invoice_row.purchase_invoice
        )


        for item in pi.items:

            taxes.append({
                "description": f"{pi.name} - {item.item_name}",
                "amount": item.amount,
                "expense_account": item.expense_account
            })


        processed_invoices.add(
            invoice_row.purchase_invoice
        )


    # Payment Entry Costs
    for payment_row in lc.linked_payment_entries:

        if payment_row.payment_entry in processed_payments:
            continue


        pe = frappe.get_doc(
            "Payment Entry",
            payment_row.payment_entry
        )


        taxes.append({
            "description": f"{pe.name} - {pe.paid_to}",
            "amount": pe.paid_amount,
            "expense_account": pe.paid_to
        })


        processed_payments.add(
            payment_row.payment_entry
        )

    # Journal Entry Costs        
    for journal_row in lc.linked_journal_entries:
        if journal_row.journal_entry in processed_journal_entries:
            continue
        je = frappe.get_doc("Journal Entry", journal_row.journal_entry)

        for row in je.accounts:
            account_type = frappe.db.get_value(
                "Account",
                row.account,
                "account_type"
            )

            if account_type != "Expense Account":
                continue

            if row.debit_in_account_currency <= 0:
                continue

            taxes.append({
                "description": f"{je.name} - {row.account}",
                "amount": row.debit_in_account_currency,
                "expense_account": row.account
            })


    return taxes



@frappe.whitelist()
def check_reconciliation_status(voucher_type, voucher_no):
    doc = frappe.get_doc(voucher_type, voucher_no)
    clearance_date = get_clearance_date(doc)

    return {
        "is_reconciled": bool(clearance_date),
        "clearance_date": clearance_date
    }

def get_clearance_date(doc):

    # Payment Entry, Journal Entry, Purchase Invoice
    clearance_date = doc.get("clearance_date")

    if clearance_date:
        return clearance_date

    # Sales Invoice
    if doc.doctype == "Sales Invoice":
        for row in doc.get("payments", []):
            if row.clearance_date:
                return row.clearance_date


    # Bank Transaction
    if doc.doctype == "Bank Transaction":
        return doc.get("clearance_date")

    # Bank Transaction linked through allocation
    result = frappe.db.sql("""
        SELECT bt.date
        FROM `tabBank Transaction Payments` btp
        INNER JOIN `tabBank Transaction` bt
            ON bt.name = btp.parent
        WHERE
            btp.payment_document = %s
            AND btp.payment_entry = %s
            AND bt.date IS NOT NULL
        LIMIT 1
    """,
    (
        doc.doctype,
        doc.name
    ),
    as_dict=True)

    if result:
        return result[0].clearance_date

    return None


@frappe.whitelist()
def reverse_bank_reconciliation(voucher_type, voucher_no, reversal_reason):
    if not reversal_reason:
        frappe.throw(
            _("Reversal Reason is mandatory.")
        )
    doc = frappe.get_doc(voucher_type,voucher_no)
    if doc.docstatus != 1:
        frappe.throw(
            _("Only submitted documents can be reversed.")
        )
    clearance_date = get_clearance_date(doc)

    if not clearance_date:
        frappe.throw(
            _("This transaction is not reconciled.")
        )

    validate_lock_date(doc, clearance_date)
    bank_account = reverse_document_reconciliation(doc)
    unlink_bank_transactions(voucher_type, voucher_no)
    create_reversal_log(voucher_type, voucher_no, bank_account, clearance_date,reversal_reason)

    frappe.msgprint(_("Bank reconciliation reversed successfully for {0} {1}.").format(voucher_type, voucher_no))
    return {
        "success": True,
    }


def reverse_document_reconciliation(doc):
    handlers = {
        "Payment Entry": reverse_payment_entry,
        "Journal Entry": reverse_journal_entry,
        "Sales Invoice": reverse_sales_invoice,
        "Purchase Invoice": reverse_purchase_invoice,
        "Bank Transaction": reverse_bank_transaction
    }

    handler = handlers.get(doc.doctype)

    if not handler:
        frappe.throw(
            _("Reversal not supported for {0}")
            .format(doc.doctype)
        )

    return handler(doc)



# Payment Entry
def reverse_payment_entry(doc):
    bank_account = None
    if doc.payment_type == "Pay":
        bank_account = doc.paid_from
    else:
        bank_account = doc.paid_to
    frappe.db.set_value(
        "Payment Entry",
        doc.name,
        "clearance_date",
        None,
        update_modified=False
    )
    return bank_account

# Journal Entry
def reverse_journal_entry(doc):
    bank_account = None
    for row in doc.accounts:
        account_type = frappe.db.get_value(
            "Account",
            row.account,
            "account_type"
        )
        if account_type == "Bank":
            bank_account = row.account
            break
    frappe.db.set_value(
        "Journal Entry",
        doc.name,
        "clearance_date",
        None,
        update_modified=False
    )

    return bank_account



# Sales Invoice
def reverse_sales_invoice(doc):
    bank_account = None
    for row in doc.payments:
        if row.clearance_date:
            bank_account = row.account

            frappe.db.set_value(
                "Sales Invoice Payment",
                row.name,
                "clearance_date",
                None,
                update_modified=False
            )

    return bank_account

# Purchase Invoice
def reverse_purchase_invoice(doc):
    bank_account = doc.cash_bank_account

    frappe.db.set_value(
        "Purchase Invoice",
        doc.name,
        "clearance_date",
        None,
        update_modified=False
    )

    return bank_account



# Bank Transaction
def reverse_bank_transaction(doc):
    frappe.db.delete(
        "Bank Transaction Payments",
        {
            "parent": doc.name
        }
    )
    update_bank_transaction_amounts(doc.name)
    
    return doc.bank_account



# Bank Transaction Links
def unlink_bank_transactions( voucher_type, voucher_no):
    rows = frappe.get_all(
        "Bank Transaction Payments",
        filters={
            "payment_document": voucher_type,
            "payment_entry": voucher_no
        },
        fields=[
            "name",
            "parent"
        ]
    )
    for row in rows:
        frappe.delete_doc(
            "Bank Transaction Payments",
            row.name,
            ignore_permissions=True
        )

        update_bank_transaction_amounts(row.parent)

def update_bank_transaction_amounts(bank_transaction):
    """
    Recalculate Bank Transaction allocation values after reconciliation reversal.
    """

    deposit, withdrawal = frappe.db.get_value(
        "Bank Transaction",
        bank_transaction,
        ["deposit", "withdrawal"]
    )

    total_amount = flt(deposit) + flt(withdrawal)

    allocated_amount = frappe.db.sql("""
        SELECT COALESCE(SUM(allocated_amount), 0)
        FROM `tabBank Transaction Payments`
        WHERE parent = %s
    """, bank_transaction)[0][0]

    allocated_amount = flt(allocated_amount)

    unallocated_amount = total_amount - allocated_amount


    if allocated_amount <= 0:
        status = "Unreconciled"

    elif allocated_amount < total_amount:
        status = "Partially Reconciled"

    else:
        status = "Reconciled"


    frappe.db.set_value(
        "Bank Transaction",
        bank_transaction,
        {
            "allocated_amount": allocated_amount,
            "unallocated_amount": unallocated_amount,
            "status": status
        },
        update_modified=False
    )

# Validation
def validate_lock_date(doc, clearance_date):
    company = doc.get("company")
    if not company:
        return
    frozen_date = frappe.db.get_value(
        "Accounts Settings",
        None,
        "acc_frozen_upto"
    )
    if frozen_date and getdate(clearance_date) <= getdate(frozen_date):
        frappe.throw(
            _(
                "Cannot reverse reconciliation before frozen date {0}"
            ).format(frozen_date)
        )



# Audit
def create_reversal_log(voucher_type, voucher_no, bank_account, original_clearance_date, reversal_reason):
    log = frappe.new_doc(
        "Bank Reconciliation Reversal Log"
    )
    log.voucher_type = voucher_type
    log.voucher_no = voucher_no
    log.bank_account = bank_account
    log.original_clearance_date = original_clearance_date
    log.reversed_by = frappe.session.user
    log.reversal_date = now_datetime()
    log.reversal_reason = reversal_reason
    log.insert(
        ignore_permissions=True
    )


@frappe.whitelist()
def make_cash_journal_entry(doc_name):
    """
    Called via JS button. Fetches Payroll Entry by name, sums custom_cash_amount
    from linked Salary Slips, creates a Draft Journal Entry, and sets 
    custom_cash_entry_created to 1.
    """
    doc = frappe.get_doc("Payroll Entry", doc_name)

    # Prevent duplicate runs
    if doc.get("custom_cash_entry_created"):
        frappe.throw(_("Cash Entry has already been created for this Payroll Entry."))

    # 1. Validation
    if not doc.get("custom_cash_account"):
        frappe.throw(_("Please select a <b>Cash Account</b> on Payroll Entry before proceeding."))

    # 2. Get active Cash Salary Component
    cash_component = frappe.db.get_value(
        "Salary Component",
        {"custom_is_component_for_cash": 1, "disabled": 0},
        "name"
    )

    if not cash_component:
        frappe.throw(_("No enabled Salary Component with 'Is Component for Cash' checked was found."))

    # 3. Get component GL Account
    component_account = frappe.db.get_value(
        "Salary Component Account",
        {"parent": cash_component, "company": doc.company},
        "account"
    )

    if not component_account:
        frappe.throw(
            _("No GL Account set for company <b>{0}</b> in Salary Component <b>{1}</b>.")
            .format(doc.company, cash_component)
        )

    # 4. Sum custom_cash_amount from active Salary Slips
    slips = frappe.get_all(
        "Salary Slip",
        filters={"payroll_entry": doc.name, "docstatus": ["!=", 2]},
        fields=["custom_cash_amount"]
    )

    total_cash_amount = sum(flt(s.custom_cash_amount) for s in slips)

    if total_cash_amount <= 0:
        frappe.throw(_("Total cash amount is 0. No Journal Entry will be created."))

    # 5. Create Draft Journal Entry
    je = frappe.get_doc({
        "doctype": "Journal Entry",
        "voucher_type": "Cash Entry",
        "company": doc.company,
        "posting_date": doc.posting_date or frappe.utils.nowdate(),
        "user_remark": _("Draft cash distribution for Payroll Entry {0}").format(doc.name),
        "accounts": [
            {
                "account": component_account,
                "debit_in_account_currency": total_cash_amount,
                "credit_in_account_currency": 0,
                "user_remark": _("Cash salary deduction allocation")
            },
            {
                "account": doc.custom_cash_account,
                "debit_in_account_currency": 0,
                "credit_in_account_currency": total_cash_amount,
                "user_remark": _("Cash account payment credit")
            }
        ]
    })

    je.insert(ignore_permissions=True)

    # 6. Flag the Payroll Entry so the button disappears on reload
    doc.db_set("custom_cash_entry_created", 1)

    doc.db_set("custom_created_cash_journal_entry", je.name)
    
    # Return Journal Entry name to JS callback
    return je.name
