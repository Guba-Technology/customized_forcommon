# Copyright (c) 2026, Guba Technology and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate


class BulkEmployeeTransfer(Document):
	def autoname(self):
		# format BET-YYYY-MM-####
		year = nowdate()[:4]
		month = nowdate()[5:7]
		prefix = "BET-{}-{}-".format(year, month)
		last_doc = frappe.db.get_all("Bulk Employee Transfer", filters={"name": ["like", prefix + "%"]}, order_by="name desc", limit=1)
		if last_doc:
			last_number = int(last_doc[0].name.split("-")[-1])
			self.name = prefix + str(last_number + 1).zfill(4)
		else:
			self.name = prefix + "0001"
	def validate(self):
		if not self.employee_list:
			frappe.throw(_("Employee list cannot be empty. Please fetch employees first."))
		if not self.property:
			frappe.throw(_("Property cannot be empty."))
		if not self.new_value:
			frappe.throw(_("New value cannot be empty."))
		if not self.old_value:
			frappe.throw(_("Old value cannot be empty."))
		if self.new_value == self.old_value:
			frappe.throw(_("New value and Old value cannot be the same. Please select different values."))
		
	def on_submit(self):
		execute_bulk_transfer(self)
	pass


def execute_bulk_transfer(doc):
    if isinstance(doc, str):
        doc = frappe.get_doc(frappe.parse_json(doc))
    
    if not doc.employee_list:
        frappe.throw(_("Employee list is empty. Please fetch employees first."))

    doctype_to_field_map = {
        "Company": "company",
        "Designation": "designation",
        "Branch": "branch",
        "Department": "department",
        "Employee Grade": "grade",
        "Employee Step": "custom_step" 
    }

    target_field = doctype_to_field_map.get(doc.property)
    
    if not target_field:
        frappe.throw(_("Invalid property selected: {0}").format(doc.property))

    count = 0
    for row in doc.employee_list:
        if row.employee:
            frappe.db.set_value("Employee", row.employee, target_field, doc.new_value)
            
            frappe.get_doc("Employee", row.employee).add_comment(
                "Info", 
                _("Bulk Transfer: {0} updated to {1}").format(doc.property, doc.new_value)
            )
            count += 1

    frappe.db.commit()

    return {
        "status": "success",
        "message": _("Successfully updated {0} employees.").format(count)
    }