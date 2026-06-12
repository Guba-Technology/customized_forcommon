from erpnext.accounts.general_ledger import make_gl_entries
from frappe.utils.nestedset import get_descendants_of
import frappe
from frappe import _
from frappe.utils import today, flt, getdate, date_diff

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

def calculate_severance_amount(doc):
    if not doc.relieving_date or not doc.date_of_joining or not doc.custom_apply_severance_pay:
        return 0

    hr_settings = frappe.get_doc("HR Settings")
    starting_year = hr_settings.custom_severenace_pay_starting_year or 1

    basic_salary = doc.ctc or 0  # change to base if available
    if basic_salary <= 0:
        return 0

    daily_wage = basic_salary / 30

    total_days = date_diff(doc.relieving_date, doc.date_of_joining)
    full_years = int(total_days / 365)

    if full_years < starting_year:
        return 0

    if full_years <= 1:
        severance = daily_wage * 30
    else:
        severance = (daily_wage * 30) + ((full_years - 1) * 10 * daily_wage)

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