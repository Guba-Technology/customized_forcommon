import frappe
import json

def clear_onboarding_docs():
    """Deletes all Module Onboarding and Onboarding Step records safely."""
    # 1. Delete the actual documents
    frappe.db.delete("Onboarding Step")
    frappe.db.delete("Module Onboarding")
    
    # 2. Fix the User records using a valid JSON string
    # We use json.dumps to ensure the database gets '{"status": "skipped"}' or similar
    skipped_value = json.dumps({}) 
    
    frappe.db.sql("""
        UPDATE `tabUser` 
        SET onboarding_status = %s
    """, (skipped_value,))
    
    frappe.db.commit()