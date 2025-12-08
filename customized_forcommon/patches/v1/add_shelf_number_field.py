import frappe

def execute():

    # 4️⃣ Expired Warehouse (Stock Settings)
    if not frappe.db.exists("Custom Field", {"dt": "Stock Settings", "fieldname": "expired_warehouse"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Stock Settings",
            "label": "Expired Warehouse",
            "fieldname": "expired_warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "insert_after": "default_warehouse"
        }).insert(ignore_permissions=True)

    frappe.db.commit()
    asset_doc = frappe.get_doc("DocType", "Asset")
    links = asset_doc.get("links", [])

    if not any(l.link_doctype == "Asset Borrowing" for l in links):
        links.append({
            "group": "Activity",
            "link_doctype": "Asset Borrowing",
            "link_fieldname": "asset"
        })
        asset_doc.set("links", links)
        asset_doc.save(ignore_permissions=True)
        frappe.db.commit()
        print("Asset Borrowing link added to Asset DocType")
