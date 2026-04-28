import frappe
from frappe import _

def get_company_from_employee(user):
    """Finds the company associated with a user via the Employee doctype."""
    return frappe.db.get_value("Employee", {"user_id": user}, "company")

def user_query_condition(user):
    if user == "Administrator":
        return ""

    company = frappe.db.get_value("Employee", {"user_id": user}, "company")

    if not company:
        return "1=0"

    return f"""
        exists (
            select 1 from `tabEmployee`
            where `tabEmployee`.user_id = `tabUser`.name
            and `tabEmployee`.company = '{company}'
        )
    """

def validate_user_access(doc, method=None):
    if frappe.session.user == "Administrator":
        return

    my_company = get_company_from_employee(frappe.session.user)
    target_company = get_company_from_employee(doc.name)

    if not my_company or not target_company:
        return

    if my_company != target_company:
        frappe.throw(
            _("Access Denied: This user is an employee of {0}").format(target_company),
            frappe.PermissionError
        )

def has_permission(doc, ptype, user):
    if user == "Administrator":
        return True

    my_company = frappe.db.get_value("Employee", {"user_id": user}, "company")
    target_company = frappe.db.get_value("Employee", {"user_id": doc.name}, "company")

    if not my_company or not target_company:
        return False

    return my_company == target_company