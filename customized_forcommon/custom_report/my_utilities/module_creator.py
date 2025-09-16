import frappe
import os

def ensure_module_in_modules_txt(app_name, module_name):
    modules_path = os.path.join(frappe.get_app_path(app_name), "modules.txt")

    # Create file if it doesn't exist
    if not os.path.exists(modules_path):
        with open(modules_path, "w") as f:
            f.write(f"{module_name}\n")
        print(f"📄 Created modules.txt and added: {module_name}")
        return

    # Check if module is already listed
    with open(modules_path, "r") as f:
        lines = [line.strip() for line in f.readlines()]

    if module_name not in lines:
        with open(modules_path, "a") as f:
            f.write(f"{module_name}\n")
        print(f"➕ Added to modules.txt: {module_name}")

def ensure_module_exists(module_name):
    if not frappe.db.exists("Module Def", module_name):
        frappe.get_doc({
            "doctype": "Module Def",
            "module_name": module_name,
            "app_name": "customized_forcommon", 
            "custom": 0,
            "developer_mode": 1
        }).insert()
        frappe.db.commit()
        print(f"📦 Created Module: {module_name}")
def execute():
    module_name = "custom report"
    ensure_module_exists(module_name)
    ensure_module_exists(module_name)
    ensure_module_in_modules_txt("customized_forcommon", module_name)