import frappe
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice

class CustomPurchaseInvoice(PurchaseInvoice):

    def validate(self):

        super().validate()
        for row in self.custom_employee_advance_details:
            row.allocated_amount = self.grand_total

    # def on_submit(self):
    #     self.apply_employee_advances()
    #     super().on_submit()  # keep default logic unless you intend to override it entirely

    # def apply_employee_advances(self):
    #     if not self.custom_employee_advance_details:
    #         return

    #     company_doc = frappe.get_doc("Company", self.company)
    #     payable_account = company_doc.default_payable_account
    

    #     if not payable_account:
    #         frappe.throw("Default Payable Account is not set in the Company master.")

    #     for adv_row in self.custom_employee_advance_details:
    #         advance_doc = frappe.get_doc("Employee Advance", adv_row.reference_name)
    #         employee = advance_doc.employee
    #         advance_account = advance_doc.advance_account

    #         if not advance_account:
    #             frappe.throw(f"Advance account not set for Employee Advance {adv_row.reference_name}")

    #         allocated_amount = adv_row.allocated_amount
    #         if allocated_amount <= 0:
    #             continue  # skip if no allocation
    #         else:
    #             frappe.msgprint(f"Allocated amount: {allocated_amount}")

    #         # 1st GL Entry (Debit Payable)
    #         self.make_gl_entry(
    #             account=payable_account,
    #             party_type="Supplier",
    #             party=self.supplier,
    #             debit=allocated_amount,
    #             credit=0,
    #             against=advance_account,
    #             remarks=f"Paying Supplier {self.supplier} from Employee Advance {adv_row.reference_name}"
    #         )

    #         # 2nd GL Entry (Credit Advance)
    #         self.make_gl_entry(
    #             account=advance_account,
    #             party_type="Employee",
    #             party=employee,
    #             debit=0,
    #             credit=allocated_amount,
    #             against=payable_account,
    #             remarks=f"Clearing Employee Advance for {employee}"
    #         )

    #     # Optional: update status to Paid
    #     self.db_set("status", "Paid")

    # def make_gl_entry(self, account, party_type, party, debit, credit, against, remarks):
    #     frappe.get_doc({
    #         "doctype": "GL Entry",
    #         "posting_date": self.posting_date,
    #         "company": self.company,
    #         "voucher_type": "Purchase Invoice",
    #         "voucher_no": self.name,
    #         "account": account,
    #         "party_type": party_type,
    #         "party": party,
    #         "debit": debit,
    #         "credit": credit,
    #         "against": against,
    #         "remarks": remarks
    #     }).insert(ignore_permissions=True)
