import frappe


def get_item_group_inventory_account(item_code, company):

    item_group = frappe.db.get_value(
        "Item",
        item_code,
        "item_group"
    )

    if not item_group:
        return None


    account = frappe.db.get_value(
        "Item Default",
        {
            "parent": item_group,
            "company": company
        },
        "custom_default_inventory_account"
    )

    return account



def validate_inventory_account(doc, method=None):

    enabled = frappe.db.get_value(
        "Company",
        doc.company,
        "custom_enable_item_group_based_inventory"
    )

    if not enabled:
        return


    for item in doc.items:

        if not item.item_code:
            continue


        account = get_item_group_inventory_account(
            item.item_code,
            doc.company
        )


        if not account:

            item_group = frappe.db.get_value(
                "Item",
                item.item_code,
                "item_group"
            )

            frappe.throw(
                f"""
                Missing Inventory Account.  <br/>
                Item Group: <b>{item_group}</b>. <br/>
            
                Please set Custom Default Inventory Account
                in Item Group -> 'Item Group Default' table for company <b>{doc.company}</b>.
                """
            )