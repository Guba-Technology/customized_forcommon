from erpnext.accounts.general_ledger import make_gl_entries
from frappe.utils.nestedset import get_descendants_of
import frappe
from frappe import _
from frappe.utils import today, add_days, getdate

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
def run_dunning_scheduler(invoice_name):
    """Run the Dunning scheduler only for a specific Sales Invoice."""
    today_date = getdate(today())
    doc = frappe.get_doc("Sales Invoice", invoice_name)

    # Skip if no outstanding amount
    if doc.docstatus != 1 or doc.outstanding_amount <= 0:
        frappe.throw("This Sales Invoice is not valid for Dunning (must be submitted and have an outstanding amount).")

    # Skip if no custom dunning rules
    if not getattr(doc, "custom_dunning_rule", None):
        frappe.throw("No Dunning rules found for this Sales Invoice.")

    dunning_created = []
    upcoming_dunnings = []
    existing_dunning_refs = []  # collect duplicates to show later

    for row in doc.custom_dunning_rule:
        after_days = int(row.after_days)
        trigger_date = add_days(getdate(doc.due_date), after_days)

       # Catch-up condition:
        # Create dunning if trigger_date is in the past OR today
        if today_date < trigger_date:
             # Future Dunning: inform how many days remain
            remaining_days = (trigger_date - today_date).days
            if remaining_days > 0:
                upcoming_dunnings.append(str(remaining_days))
            continue

        company = frappe.get_doc("Company", doc.company)
        default_dunning_account = company.custom_default_dunning_income_account

        # --- Duplicate check (parent + child table) ---
        existing_dunnings = frappe.get_all(
            "Dunning",
            filters={
                "company": doc.company,
                "customer": doc.customer,
                "currency": doc.currency,
                "dunning_fee": row.dunning_fee,
                "custom_auto_created": 1,
            },
            fields=["name"]
        )

        duplicate_found = None
        for d in existing_dunnings:
            existing_doc = frappe.get_doc("Dunning", d.name)
            for pay in existing_doc.overdue_payments:
                if (
                    pay.sales_invoice == doc.name
                    and float(pay.outstanding) == float(doc.outstanding_amount)
                    and getdate(pay.due_date) == getdate(doc.due_date)
                ):
                    duplicate_found = existing_doc.name
                    break
            if duplicate_found:
                break

        if duplicate_found:
            existing_dunning_refs.append(duplicate_found)
            continue

        # --- Create new Dunning ---
        dunning_doc = frappe.get_doc({
            "doctype": "Dunning",
            "company": doc.company,
            "customer": doc.customer,
            "currency": doc.currency,
            "posting_date": trigger_date,
            "dunning_fee": row.dunning_fee,
            "conversion_rate": 1.0,
            "custom_auto_created": 1,
            "overdue_payments": [
                {
                    "sales_invoice": doc.name,
                    "outstanding": doc.outstanding_amount,
                    "due_date": doc.due_date,
                }
            ],
        })
        dunning_doc.insert(ignore_permissions=True)

        if row.dunning_state and row.dunning_state == "Submitted":
            dunning_doc.submit()

        dunning_created.append(str(after_days))

    frappe.db.commit()

    # --- Build response message ---
    if dunning_created:
        days_text = ", ".join(dunning_created)
        return f"Dunning successfully created for {invoice_name} (overdue by {days_text} day(s))."
    elif existing_dunning_refs:
        existing_text = ", ".join(existing_dunning_refs)
        return f"A Dunning already exists for {invoice_name}: {existing_text}"
    elif upcoming_dunnings:
        upcoming_text = ", ".join(upcoming_dunnings)
        return f"No Dunning applied today for {invoice_name}. Dunning will be applied in {upcoming_text} day(s)."
    else:
        return f"No Dunning applicable today for {invoice_name}."

