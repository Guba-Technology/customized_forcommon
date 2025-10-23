import frappe
from erpnext.accounts.doctype.gl_entry.gl_entry import GLEntry

def custom_validate_party(self):
    account_type = frappe.get_cached_value("Account", self.account, "account_type")

    if account_type in ["Receivable", "Payable"]:
        if not (self.party_type and self.party):
            frappe.throw(
                f"Row {self.idx}: Party Type and Party is required for Receivable / Payable account {self.account}"
            )
    # Enforce Cash only if Party Type is Employee (Employee Advance)
    elif account_type == "Cash" and self.party_type == "Employee":
        if not self.party:
            frappe.throw(
                f"Row {self.idx}: Party is required for Cash account {self.account} when Party Type is Employee"
            )
    else:
        # clear party fields for non-receivable/payable accounts
        self.party_type = None
        self.party = None

GLEntry.validate_party = custom_validate_party
