import frappe
import logging

logger = logging.getLogger(__name__)

def update_stock_ledger_with_department(doc, method=None):
    try:
        custom_dept = doc.custom_department
        if not custom_dept:
            return
        frappe.db.sql("""
            UPDATE `tabStock Ledger Entry`
            SET custom_department = %s
            WHERE voucher_type = 'Purchase Receipt' AND voucher_no = %s
        """, (custom_dept, doc.name))
        frappe.db.commit()
    except Exception as e:
        logger.error(f"Failed to update Stock Ledger Entries with custom_department: {e}")
