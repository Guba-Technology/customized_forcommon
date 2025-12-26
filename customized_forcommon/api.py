from erpnext.accounts.general_ledger import make_gl_entries
from frappe.utils.nestedset import get_descendants_of
import frappe
from frappe import _
from frappe.utils import today

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



