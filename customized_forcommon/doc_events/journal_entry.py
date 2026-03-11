import frappe
def make_reversed(doc, method):
    journal_entry = frappe.get_doc("Journal Entry", doc.reversal_of)
    journal_entry.custom_reversed = 1
    journal_entry.save()
    