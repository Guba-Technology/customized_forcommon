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
    "Home", "Sales and Marketing", "Human Resource", "Inventory", "Purchase",
    "Accounting & Finance", "Payables", "Receivables", "Financial Reports", "Users", "Settings", "Recruitment", "Employee Lifecycle", 
    "Performance","Shift & Attendance", "Expense Claim", "Leaves", "Payroll",
    "Salary Payout", "Tax & Benefits",
]
LIT_MODULES = [
    "Accounts", "Stock", "Buying", "Selling", "HR", "Payroll", 
    "Setup", "Core", "Custom", "Desk", "Email", "Automation", "Common Customization","Contacts"
]
HIDDEN_BY_DEFAULT = ["CRM", "Quality Management", "Quality", "Projects", "Assets", "Manufacturing"]
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
    allowed_mod_str = frappe.db.get_global("lite_modules")
    allowed_modules = json.loads(allowed_mod_str) if allowed_mod_str else LIT_MODULES
    
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
    
    # Restore every module recorded in the manifest
    for module_name in list(manifest.keys()):
        toggle_module_visibility(module_name, hide=False)

    # Global reset for any stragglers
    frappe.db.sql("UPDATE `tabDocType` SET read_only = 0, show_name_in_global_search = 1 WHERE custom = 0")
    if frappe.db.has_column("Module Def", "disabled"):
        frappe.db.sql("UPDATE `tabModule Def` SET disabled = 0")

    # Unhide all Workspaces and force a reload from original JSON to restore 'content'
    workspaces = frappe.get_all("Workspace", fields=["name", "module"])
    for ws in workspaces:
        frappe.db.set_value("Workspace", ws.name, "is_hidden", 0, update_modified=False)
        try:
            app = frappe.db.get_value("Module Def", ws.module, "app_name")
            if app:
                reload_doc(frappe.scrub(app), "desktop_page", frappe.scrub(ws.name), force=True)
        except: pass
    
    # Clear manifest file instead of deleting to maintain file presence
    write_manifest({})
    
    frappe.db.commit()
    frappe.clear_cache()

def toggle_module_visibility(module_name, hide=True):
    """Surgical toggle that records original state before hiding."""
    manifest = read_manifest()
    
    if hide:
        # --- SNAPSHOT PHASE ---
        if module_name not in manifest:
            # Record Module State
            mod_disabled = 0
            if frappe.db.has_column("Module Def", "disabled"):
                mod_disabled = frappe.db.get_value("Module Def", module_name, "disabled") or 0
            
            # Record DocType States
            doctypes_meta = {}
            dts = frappe.get_all("DocType", filters={"module": module_name}, fields=["name", "read_only", "show_name_in_global_search"])
            for d in dts:
                doctypes_meta[d.name] = {"read_only": d.read_only, "show_name_in_global_search": d.show_name_in_global_search}
            
            # Record Workspace States (including full content)
            workspaces_meta = {}
            wss = frappe.get_all("Workspace", filters={"module": module_name}, fields=["name", "is_hidden", "content"])
            for w in wss:
                workspaces_meta[w.name] = {"is_hidden": w.is_hidden, "content": w.content}

            manifest[module_name] = {
                "module_disabled": mod_disabled,
                "doctypes_meta": doctypes_meta,
                "workspaces_meta": workspaces_meta,
                "reports": frappe.get_all("Report", filters={"module": module_name}, pluck="name"),
                "pages": frappe.get_all("Page", filters={"module": module_name}, pluck="name")
            }

        # --- APPLY PHASE ---
        if frappe.db.has_column("Module Def", "disabled"):
            frappe.db.set_value("Module Def", module_name, "disabled", 1)
        
        frappe.db.sql("UPDATE `tabDocType` SET read_only=1, show_name_in_global_search=0 WHERE module=%s", module_name)
        frappe.db.sql("UPDATE `tabWorkspace` SET is_hidden=1 WHERE module=%s", module_name)

    else:
        # --- RESTORE PHASE ---
        if module_name in manifest:
            data = manifest[module_name]
            
            # Restore Module
            if frappe.db.has_column("Module Def", "disabled"):
                frappe.db.set_value("Module Def", module_name, "disabled", data.get("module_disabled", 0))
            
            # Restore DocTypes exactly as they were
            for dt_name, meta in data.get("doctypes_meta", {}).items():
                frappe.db.set_value("DocType", dt_name, meta, update_modified=False)
            
            # Restore Workspaces exactly as they were (including content/shortcuts)
            for ws_name, meta in data.get("workspaces_meta", {}).items():
                frappe.db.set_value("Workspace", ws_name, meta, update_modified=False)
            
            manifest.pop(module_name)

    write_manifest(manifest)
    frappe.db.commit()
    frappe.clear_cache()
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
    # Bulk update for standard hidden modules
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