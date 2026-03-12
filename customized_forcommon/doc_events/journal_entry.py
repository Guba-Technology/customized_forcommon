import frappe

def make_reversed(doc, method):
    if not doc.reversal_of:
        return

    if frappe.db.exists("Journal Entry", doc.reversal_of):
        journal_entry = frappe.get_doc("Journal Entry", doc.reversal_of)
        journal_entry.custom_reversed = 1
        journal_entry.save(ignore_permissions=True)