import frappe

def delete_old_material_request_client_scripts():
    client_script_names = [
        'Adding "Material Cost" option in Purpose',
    ]

    for client_script_name in client_script_names:
        if not frappe.db.exists("Client Script", client_script_name):
            continue

        client_script = frappe.get_doc(
            "Client Script",
            client_script_name
        )

        if client_script.dt != "Material Request":
            continue

        frappe.delete_doc(
            "Client Script",
            client_script_name,
            force=True
        )