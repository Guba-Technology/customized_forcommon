# in your_app/your_app/doctype/user/user.py
import frappe
from frappe import _

def validate_birth_date(doc, method):
    from frappe.utils import getdate, today

    if doc.birth_date:
        if getdate(doc.birth_date) > getdate(today()):
            frappe.throw(_("Birth Date cannot be in the future"))

        # Optional: minimum age 18
        age = getdate(today()).year - getdate(doc.birth_date).year
        if age < 18:
            frappe.throw(_("User must be at least 18 years old"))