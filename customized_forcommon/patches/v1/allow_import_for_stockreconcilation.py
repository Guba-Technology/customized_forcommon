import frappe

def execute():
    try:
        doc = frappe.get_doc("DocType", "Stock Reconciliation")
        doc.allow_import = 1
        doc.save()
        frappe.db.commit()
        frappe.logger().info("Import enabled on Stock Reconciliation")
    except Exception as e:
        frappe.log_error(message=str(e), title="Patch failed: Enable import on Stock Reconciliation")
        raise
