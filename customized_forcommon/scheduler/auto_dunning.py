import frappe
from frappe.utils import today, add_days, getdate

def daily_dunning_scheduler():
    today_date = getdate(today())  # Today's date as datetime.date

    # Get all Sales Invoices with outstanding amounts and due date <= today
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "docstatus": 1,
            "outstanding_amount": [">", 0],
            "due_date": ["<=", today_date]
        },
        fields=[
            "name", "due_date", "customer", "company", "currency", "outstanding_amount"
        ]
    )

    for inv in invoices:
        doc = frappe.get_doc("Sales Invoice", inv.name)

        # Skip if no custom dunning rules
        if not getattr(doc, "custom_dunning_rule", None):
            continue

        for row in doc.custom_dunning_rule:
            after_days = int(row.after_days)

            # Calculate trigger date for this rule
            trigger_date = add_days(getdate(doc.due_date), after_days)

           # Create dunning if trigger_date is in the past OR today (catch-up)
            if trigger_date < today_date:
                continue

            # Fetch company and its default dunning income account
            company = frappe.get_doc("Company", doc.company)
            default_dunning_account = company.custom_default_dunning_income_account

            # DUPLICATE CHECK: parent + child table matching fields
            existing_dunnings = frappe.get_all(
                "Dunning",
                filters={
                    "company": doc.company,
                    "customer": doc.customer,
                    "currency": doc.currency,
                    "posting_date": trigger_date,
                    "dunning_fee": row.dunning_fee,
                    "conversion_rate": 1.0,
                    "custom_auto_created": 1,
                },
                fields=["name"]
            )

            duplicate_found = False

            for d in existing_dunnings:
                existing_doc = frappe.get_doc("Dunning", d.name)
                for pay in existing_doc.overdue_payments:
                    if (
                        pay.sales_invoice == doc.name
                        and float(pay.outstanding) == float(doc.outstanding_amount)
                        and getdate(pay.due_date) == getdate(doc.due_date)
                    ):
                        duplicate_found = True
                        frappe.logger().info(
                            f"Skipped duplicate Dunning for invoice {doc.name} on {trigger_date}"
                        )
                        break
                if duplicate_found:
                    break

            if duplicate_found:
                continue

            # --- Create new Dunning ---
            dunning_doc = frappe.get_doc({
                "doctype": "Dunning",
                "company": doc.company,
                "customer": doc.customer,
                "currency": doc.currency,
                "posting_date": trigger_date,  
                "dunning_fee": row.dunning_fee,
                "conversion_rate": 1.0,
                "custom_auto_created": 1,
                "overdue_payments": [
                    {
                        "sales_invoice": doc.name,
                        "outstanding": doc.outstanding_amount,
                        "due_date": doc.due_date  # required to calculate overdue_days
                    }
                ],
                "income_account": default_dunning_account or None
            })
            dunning_doc.insert(ignore_permissions=True)

            # Auto-submit if rule says so
            if row.dunning_state and row.dunning_state == "Submitted":
                dunning_doc.save(ignore_permissions=True)
                dunning_doc.submit()

        # Save changes in Sales Invoice
        doc.save(ignore_permissions=True)

    # Commit all changes once at the end
    frappe.db.commit()
