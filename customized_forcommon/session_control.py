import frappe

def single_session(login_manager):
    user = login_manager.user

    if not user or user == "Guest":
        return

    current_sid = frappe.session.sid

    frappe.db.sql("""
        DELETE FROM `tabSessions`
        WHERE user=%s
        AND sid != %s
        AND status='Active'
    """, (user, current_sid))

    frappe.db.commit()