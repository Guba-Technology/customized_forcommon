import frappe

def execute():
    if not frappe.db.exists("Custom Field", "Payment Entry-paid_by"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Payment Entry",
            "fieldname": "paid_by",
            "label": "Paid By",
            "fieldtype": "Link",
            "options": "Employee",
            "insert_after": "paid_from",
            "read_only": 0,
            "no_copy": 0,
            "fetch_from": "",
            "depends_on": "eval:doc.paid_from"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
