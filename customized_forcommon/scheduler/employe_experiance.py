import frappe
def calculate_experience():
    frappe.db.sql("""
        UPDATE `tabEmployee`
        SET custom_total_working_experience = CONCAT(
            FLOOR(PERIOD_DIFF(
                EXTRACT(YEAR_MONTH FROM COALESCE(relieving_date, CURDATE())), 
                EXTRACT(YEAR_MONTH FROM date_of_joining)
            ) / 12),
            '.',
            MOD(PERIOD_DIFF(
                EXTRACT(YEAR_MONTH FROM COALESCE(relieving_date, CURDATE())), 
                EXTRACT(YEAR_MONTH FROM date_of_joining)
            ), 12),
            ' Years'
        )
        WHERE status = 'Active' 
          AND date_of_joining IS NOT NULL
    """)
    
    frappe.db.commit()