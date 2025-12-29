import frappe
from frappe.model.document import Document

class TalentManagement(Document):
    pass

@frappe.whitelist()
def create_connections(talent_doc):
    res = frappe.db.sql("""
        SELECT p.status, c.employee 
        FROM `tabTalent Management` p
        JOIN `tabSuccession Planning Details` c ON c.parent = p.name
        WHERE p.name = %s LIMIT 1
    """, talent_doc, as_dict=1)
	
    if not res or not res[0].employee:
        return

    status, employee = res[0].status, res[0].employee
    connections = ["Employee Promotion", "Employee Transfer", "Employee Onboarding", "Employee Incentive"]

    for doctype in connections:
        if status == "Completed":
            frappe.db.sql("""
                UPDATE `tab{0}` 
                SET custom_talent_management_reference = %s 
                WHERE employee = %s
            """.format(doctype), (talent_doc, employee))
        else:
            frappe.db.sql("""
                UPDATE `tab{0}` 
                SET custom_talent_management_reference = NULL 
                WHERE employee = %s AND custom_talent_management_reference = %s
            """.format(doctype), (employee, talent_doc))