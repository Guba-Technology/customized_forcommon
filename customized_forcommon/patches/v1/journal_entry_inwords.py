import frappe

def execute():
    doctype = "Journal Entry"
    fieldname = "total_amount_in_words"

    # 1. Update fieldtype in DocField (for core field)
    frappe.db.sql("""
        UPDATE `tabDocField`
        SET fieldtype = 'Small Text'
        WHERE parent = %s AND fieldname = %s
    """, (doctype, fieldname))

    # 2. Update fieldtype in Custom Field table (if exists)
    frappe.db.sql("""
        UPDATE `tabCustom Field`
        SET fieldtype = 'Small Text'
        WHERE dt = %s AND fieldname = %s
    """, (doctype, fieldname))

    # 3. Commit current transaction BEFORE running ALTER TABLE
    frappe.db.commit()

    # 4. Run ALTER TABLE directly using raw connection (avoiding ImplicitCommitError)
    conn = frappe.db.get_connection()
    cursor = conn.cursor()
    cursor.execute(f"ALTER TABLE `tab{doctype}` MODIFY COLUMN `{fieldname}` TEXT;")
    conn.commit()
    cursor.close()

    frappe.logger().info(f"✅ Updated {doctype}.{fieldname} to Small Text (TEXT column)")
