import frappe

def execute():
    doctype = "Asset"
    fieldname = "status"
    new_option = "Borrowed"

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
    # Get field definition
    df = frappe.get_meta(doctype).get_field(fieldname)
    if not df:
        frappe.log_error("Field 'status' not found in Asset doctype")
        return

    # Convert options to list
    options = df.options.split("\n") if df.options else []

    # Avoid duplicates
    if new_option not in options:
        options.append(new_option)
        updated_options = "\n".join(options)

        # Create property setter
        frappe.make_property_setter({
            "doctype": doctype,
            "fieldname": fieldname,
            "property": "options",
            "value": updated_options,
            "property_type": "Text"
        })


        frappe.db.commit()
        print(f"✔ Added '{new_option}' to Asset.status")
    else:
        print("✔ 'Borrowed' already exists")

