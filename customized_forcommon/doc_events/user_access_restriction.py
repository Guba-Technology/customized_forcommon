import frappe
from frappe import _

def get_company_from_employee(user):
    """Finds the company associated with a user via the Employee doctype."""
    return frappe.db.get_value("Employee", {"user_id": user}, "company")

def user_query_condition(user):
    """Filters the User List by joining with the Employee table."""
    if user == "Administrator":
        return ""
    
    company = get_company_from_employee(user)
    
    if company:
        # Filter users who have an Employee record linked to the same company
        return f"""exists (
            select name from `tabEmployee` 
            where `tabEmployee`.user_id = `tabUser`.name 
            and `tabEmployee`.company = '{company}'
        )"""
    
    # If the manager isn't an Employee or has no company, show nothing
    return "1=0"

def validate_user_access(doc, method=None):
    """Ensures a System Manager can't open a User form from another company."""
    if frappe.session.user == "Administrator":
        return
        
    my_company = get_company_from_employee(frappe.session.user)
    target_company = get_company_from_employee(doc.name)
    
    if my_company and target_company and my_company != target_company:
        frappe.throw(_("Access Denied: This user is an employee of {0}").format(target_company), frappe.PermissionError)