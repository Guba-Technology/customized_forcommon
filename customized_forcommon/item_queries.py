import frappe

@frappe.whitelist()
def get_items_by_warehouse(doctype, txt, searchfield, start, page_len, filters):
    warehouse = filters.get("warehouse")
    company = filters.get("company")

    if not warehouse:
        return []

    return frappe.db.sql(
        """
        SELECT DISTINCT
            i.name AS item_code,
            i.item_name
        FROM `tabItem` i
        LEFT JOIN `tabBin` b
            ON b.item_code = i.name
            AND b.warehouse = %(warehouse)s
        LEFT JOIN `tabItem Default` id
            ON id.parent = i.name
            AND id.default_warehouse = %(warehouse)s
            {company_condition}
        WHERE
            i.is_stock_item = 1
            AND (
                IFNULL(b.actual_qty, 0) > 0
                OR IFNULL(b.projected_qty, 0) > 0
                OR id.default_warehouse IS NOT NULL
            )
            AND (
                i.name LIKE %(txt)s
                OR i.item_name LIKE %(txt)s
            )
        ORDER BY i.name
        LIMIT %(start)s, %(page_len)s
        """.format(
            company_condition="AND id.company = %(company)s" if company else ""
        ),
        {
            "warehouse": warehouse,
            "company": company,
            "txt": f"%{txt}%",
            "start": start,
            "page_len": page_len,
        },
        as_list=True,
    )
