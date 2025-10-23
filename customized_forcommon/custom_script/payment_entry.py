import frappe

@frappe.whitelist()
def get_cash_employees(paid_from_account):
    # Get all Employee Advance linked via Payment Entry Reference
    advances = frappe.get_all(
        "Employee Advance",
        filters={"docstatus": 1},  # only submitted
        fields=["employee", "name"]
    )

    # Now filter only those that have a Payment Entry to the selected cash account
    employees = []
    for adv in advances:
        pe_refs = frappe.get_all(
            "Payment Entry Reference",
            filters={"reference_name": adv.name, "docstatus": 1},
            fields=["parent"]
        )
        for pe_ref in pe_refs:
            pe_doc = frappe.get_doc("Payment Entry", pe_ref.parent)
            if pe_doc.paid_from == paid_from_account:
                employees.append(adv.employee)
    return list(set(employees))
