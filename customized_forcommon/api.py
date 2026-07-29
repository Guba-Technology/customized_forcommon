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