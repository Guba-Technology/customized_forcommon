import frappe
from frappe.utils import add_days, today, formatdate

def notify_expiring_contracts():
    target_date = add_days(today(), 7)
    
    expiring_employees = frappe.get_all("Employee", 
        filters={
            "contract_end_date": target_date,
            "status": "Active"
        },
        fields=["name", "employee_name", "user_id", "contract_end_date", "designation"]
    )

    if not expiring_employees:
        return

    for emp in expiring_employees:
        recipients = ["Administrator"]
        if emp.user_id:
            recipients.append(emp.user_id)
        
        formatted_date = formatdate(emp.contract_end_date)

        subject = f"🔔 Contract Expiry Alert: {emp.employee_name}"
        message = f"""
            <h3>Contract Expiration Notice</h3>
            <p>This is an automated reminder that the employment contract for <b>{emp.employee_name}</b> ({emp.designation or 'Staff'}) is scheduled to expire on <b>{formatted_date}</b>.</p>
            <p>Please take the necessary actions regarding renewal or documentation.</p>
            <hr>
            <small>Document ID: {emp.name}</small>
        """

        for user in recipients:
            # Check if notification already exists for today to avoid spamming on manual reruns
            if not frappe.db.exists("Notification Log", {"for_user": user, "document_name": emp.name, "attached_to_name": emp.name, "creation": [">", today()]}):
                
                notification = frappe.new_doc("Notification Log")
                notification.for_user = user
                notification.subject = subject
                notification.email_content = message
                notification.document_type = "Employee"
                notification.document_name = emp.name
                notification.insert(ignore_permissions=True)
        
    frappe.db.commit()