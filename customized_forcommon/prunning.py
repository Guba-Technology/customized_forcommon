"""
Utility to prune Frappe/ERPNext to LITE mode.
Handles Workspace pruning, DocType metadata locking, and URL-based security.
"""
import frappe
import json
import os
from frappe.modules import reload_doc 
from frappe import _

# Configuration
ALLOWED_WORKSPACES = [
    "Home", "Inventory",
    "Accounting & Finance", "Payables", "Receivables", "Manufacturing",
    "Financial Reports", "Users", "Settings","Welcome Workspace"
]
frapp_modules =frappe.get_all("Module Def", pluck="name", filters ={"app_name": "frappe"})
LIT_MODULES = [
    "Accounts", "Stock", "Manufacturing",
    "Setup", "Core", "Custom", "Desk", "Email", "Automation", "Common Customization","Contacts"
]
LIT_MODULES.extend(frapp_modules)
HIDDEN_BY_DEFAULT = ["CRM", "Quality Management", "Quality", "Projects", "Assets", "HR", "Buying", "Selling"]
MANIFEST_FILE = "lite_mode_lock_manifest.json"

def get_manifest_path():
    return os.path.join(frappe.get_site_path(), MANIFEST_FILE)

def read_manifest():
    path = get_manifest_path()
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def write_manifest(data):
    path = get_manifest_path()
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

@frappe.whitelist()
def get_locked_manifest():
    """Returns a comprehensive list of locked components for the JS Locker."""
    data = read_manifest()
    if not data:
        return {"modules": [], "doctypes": [], "reports": [], "pages": []}
    
    all_doctypes, all_reports, all_pages = [], [], []
    
    # We now iterate through the snapshot to extract names for the JS locker
    for mod, snapshot in data.items():
        if isinstance(snapshot, dict):
            all_doctypes.extend(snapshot.get("doctypes_meta", {}).keys())
            all_reports.extend(snapshot.get("reports", []))
            all_pages.extend(snapshot.get("pages", []))

    return {
        "modules": list(data.keys()),
        "doctypes": list(set(all_doctypes)),
        "reports": list(set(all_reports)),
        "pages": list(set(all_pages))
    }
@frappe.whitelist()
def run(mode="lite"):
    is_lite = (mode == "lite")
    print(f"Switching to {mode.upper()} mode...")
    try:
        if is_lite:
            apply_lite_mode()
        else:
            restore_full_mode()
        
        frappe.clear_cache()
        print(f"Successfully updated to {mode.upper()} mode.")
        return True
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "LITE Mode Toggle Error")
        print(f"Error: {e}")
        return False

def apply_lite_mode():
    """Bulk apply Lite mode while creating snapshots."""
    # 1. Handle Module Selections
    
    allowed_modules = LIT_MODULES
    
    modules = frappe.get_all("Module Def", pluck="name")
    for mod in modules:
        if mod not in allowed_modules:
            toggle_module_visibility(mod, hide=True)
            frappe.db.sql("DELETE FROM `tabRoute History` WHERE route LIKE %s", f"/app/{mod.lower()}%")
    
    # 2. Handle Workspace Visibility based on ALLOWED_WORKSPACES
    workspaces = frappe.get_all("Workspace", fields=["name", "label"])
    for ws in workspaces:
        label = ws.label or ws.name
        if label not in ALLOWED_WORKSPACES:
            # We don't use toggle_module_visibility here because these are standalone workspaces
            frappe.db.set_value("Workspace", ws.name, "is_hidden", 1, update_modified=False)

    toggle_metadata(True)

def restore_full_mode():
    """Precision restore using the manifest snapshots."""
    manifest = read_manifest()
    
    # 1. Restore modules recorded in manifest
    for module_name in list(manifest.keys()):
        toggle_module_visibility(module_name, hide=False)

    # 2. Global reset for Workspaces
    # We set is_hidden to 0 AND public to 1 to ensure visibility in the sidebar
    frappe.db.sql("UPDATE `tabWorkspace` SET is_hidden = 0, public = 1")
    
    # 3. Clear manifest and cache
    write_manifest({})
    frappe.db.commit()
    frappe.clear_cache()

def toggle_module_visibility(module_name, hide=True):
    """Selective toggle for a single module's visibility and URL security."""
    status = 1 if hide else 0
    search = 0 if hide else 1

    if frappe.db.has_column("Module Def", "disabled"):
        frappe.db.set_value("Module Def", module_name, "disabled", status)

    frappe.db.sql("UPDATE `tabDocType` SET read_only=%s, show_name_in_global_search=%s WHERE module=%s", (status, search, module_name))
    frappe.db.sql("UPDATE `tabWorkspace` SET is_hidden=%s WHERE module=%s", (status, module_name))
    
    # Sync with URL locker manifest
    toggle_structure_lock(module_name, lock=hide)
    
    frappe.db.commit()
    frappe.clear_cache()
    frappe.msgprint(_(f"Module '{module_name}' is now {'Hidden/Locked' if hide else 'Visible/Unlocked'}."), alert=True)
    print(f"Module '{module_name}' is now {'Hidden/Locked' if hide else 'Visible/Unlocked'}.")

def toggle_structure_lock(module_name, lock=True):
    path = get_manifest_path()
    all_locked_data = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            try: all_locked_data = json.load(f)
            except: all_locked_data = {}

    if lock:
        all_locked_data[module_name] = {
            "doctypes": frappe.get_all("DocType", filters={"module": module_name}, pluck="name"),
            "reports": frappe.get_all("Report", filters={"module": module_name}, pluck="name"),
            "pages": frappe.get_all("Page", filters={"module": module_name}, pluck="name")
        }
    else:
        all_locked_data.pop(module_name, None)

    with open(path, "w") as f:
        json.dump(all_locked_data, f, indent=4)

def toggle_metadata(is_lite):
    status, search = (1, 0) if is_lite else (0, 1)
    frappe.db.sql("""UPDATE `tabDocType` SET read_only = %s, show_name_in_global_search = %s 
                     WHERE (module IN %s OR (module NOT IN %s AND %s = 1)) AND custom = 0""", 
                  (status, search, tuple(HIDDEN_BY_DEFAULT), tuple(LIT_MODULES), status))
    frappe.db.sql("""UPDATE `tabDashboard` SET is_standard = %s WHERE module IN %s""", (0 if is_lite else 1, tuple(HIDDEN_BY_DEFAULT)))
    frappe.db.commit()

@frappe.whitelist()
def get_init_data():
    """Fetches current state based on detailed Snapshot manifest."""
    data = read_manifest()
    all_mods = frappe.get_all("Module Def", pluck="name")
    
    locked_modules = list(data.keys())
    locked_doctypes = []
    locked_reports = []
    locked_pages = []

    for mod, snapshot in data.items():
        locked_doctypes.extend(snapshot.get("doctypes_meta", {}).keys())
        locked_reports.extend(snapshot.get("reports", []))
        locked_pages.extend(snapshot.get("pages", []))

    settings = {
        "lite_modules": [m for m in all_mods if m not in locked_modules],
        "locked_doctypes": list(set(locked_doctypes)),
        "locked_reports": list(set(locked_reports)),
        "locked_pages": list(set(locked_pages)),
        "allowed_workspaces": frappe.get_all("Workspace", filters={"label": ["in", ALLOWED_WORKSPACES]}, pluck="name")
    }

    return {
        "workspaces": frappe.get_all("Workspace", pluck="name"),
        "modules": all_mods,
        "settings": settings,
        "is_lite": 'LITE' if len(locked_modules) > 0 else 'FULL'
    }

@frappe.whitelist()
def save_settings(workspaces=None, modules=None):
    if workspaces is not None:
        frappe.db.set_global("lite_allowed_workspaces", json.dumps(workspaces))
    if modules is not None:
        frappe.db.set_global("lite_modules", json.dumps(modules))
    frappe.db.commit()
    return "Settings Saved"

@frappe.whitelist()
def get_system_summary():
    return {
        "hidden_workspaces": frappe.get_all("Workspace", filters={"is_hidden": 1}, pluck="name"),
        "readonly_doctypes": frappe.get_all("DocType", filters={"read_only": 1}, pluck="name"),
        "locked_modules": list(read_manifest().keys())
    }

def print_status():
    summary = get_system_summary()
    print(f"System Mode: {'LITE' if summary['locked_modules'] else 'FULL'}")
    print(f"Hidden Workspaces: {len(summary['hidden_workspaces'])}")
    print(f"Locked Modules: {len(summary['locked_modules'])}")
@frappe.whitelist()
def toggle_module_visibility_from_gui(module_name, hide):
    hide = bool(int(hide))
    toggle_module_visibility(module_name, hide)