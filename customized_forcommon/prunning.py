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
    "Accounting & Finance", "Users", "Settings", "Recruitment", "Employee Lifecycle", 
    "Performance","Shift & Attendance", "Expense Claim", "Leaves", "Payroll",
    "Salary Payout", "Tax & Benefits",
]
LIT_MODULES = [
    "Accounts", "Stock", "Buying", "Selling", "HR", "Payroll", 
    "Setup", "Core", "Custom", "Desk", "Email", "Automation", "Common Customization",
]
HIDDEN_BY_DEFAULT = ["CRM", "Quality Management", "Quality", "Projects", "Assets", "Manufacturing"]
MANIFEST_FILE = "lite_mode_lock_manifest.json"

def get_manifest_path():
    return os.path.join(frappe.get_site_path(), MANIFEST_FILE)

@frappe.whitelist()
def get_locked_manifest():
    """Returns a comprehensive list of locked components for the JS Locker."""
    path = get_manifest_path()
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                data = json.load(f)
            except:
                return {"modules": [], "doctypes": [], "reports": [], "pages": []}
            
            all_doctypes, all_reports, all_pages = [], [], []
            
            for mod, components in data.items():
                # Handle dictionary format (New) or list format (Old)
                if isinstance(components, dict):
                    all_doctypes.extend(components.get("doctypes", []))
                    all_reports.extend(components.get("reports", []))
                    all_pages.extend(components.get("pages", []))
                elif isinstance(components, list):
                    all_doctypes.extend(components)

            return {
                "modules": list(data.keys()),
                "doctypes": list(set(all_doctypes)),
                "reports": list(set(all_reports)),
                "pages": list(set(all_pages))
            }
    return {"modules": [], "doctypes": [], "reports": [], "pages": []}
@frappe.whitelist()
def run(mode="lite"):
    is_lite = (mode == "lite")
    print(f"Switching to {mode.upper()} mode...")
    try:
        if is_lite:
            apply_lite_mode()
            return True
        else:
            restore_full_mode()
            return True
        frappe.clear_cache()
        print(f"Successfully updated to {mode.upper()} mode.")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "LITE Mode Toggle Error")
        print(f"Error: {e}")

def apply_lite_mode():
    workspaces = frappe.get_all("Workspace", fields=["name", "module", "label"])
    allowed_dts = frappe.get_all("DocType", filters={"module": ["in", LIT_MODULES]}, pluck="name")
    
    for ws in workspaces:
        label = ws.label or ws.name
        is_hidden = 0 if label in ALLOWED_WORKSPACES else 1
        frappe.db.set_value("Workspace", ws.name, "is_hidden", is_hidden, update_modified=False)

        if not is_hidden:
            # Clean up Workspace Links and Shortcuts
            frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent=%s AND link_to NOT IN %s AND type!='Card Break'", (ws.name, tuple(allowed_dts + [""])))
            frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent=%s AND link_to NOT IN %s", (ws.name, tuple(allowed_dts + [""])))
            
            content = frappe.db.get_value("Workspace", ws.name, "content")
            if content:
                try:
                    data = json.loads(content)
                    clean_data = [b for b in data if not (b.get("data", {}).get("link_to") or b.get("data", {}).get("shortcut_name")) 
                                  or (b.get("data", {}).get("link_to") in allowed_dts) 
                                  or (b.get("data", {}).get("shortcut_name") in allowed_dts)]
                    frappe.db.set_value("Workspace", ws.name, "content", json.dumps(clean_data), update_modified=False)
                except: pass

    modules = frappe.get_all("Module Def", pluck="name")
    for mod in modules:
        if mod not in LIT_MODULES:
            toggle_structure_lock(mod, lock=True)
            frappe.db.sql("""
            DELETE FROM `tabRoute History`
            WHERE route = %s """, f"/app/{mod.lower()}")
    toggle_metadata(True)

def restore_full_mode():
    frappe.db.sql("UPDATE `tabDocType` SET read_only = 0, show_name_in_global_search = 1 WHERE custom = 0")
    if frappe.db.has_column("Module Def", "disabled"):
        frappe.db.sql("UPDATE `tabModule Def` SET disabled = 0")
    
    # Remove all entries from manifest
    path = get_manifest_path()
    if os.path.exists(path):
        os.remove(path)

    workspaces = frappe.get_all("Workspace", fields=["name", "module"])
    for ws in workspaces:
        frappe.db.set_value("Workspace", ws.name, "is_hidden", 0, update_modified=False)
        try:
            app = frappe.db.get_value("Module Def", ws.module, "app_name")
            if app:
                reload_doc(frappe.scrub(app), "desktop_page", frappe.scrub(ws.name), force=True)
        except: pass
    
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
    """Fetches current state and determines mode based on JSON content."""
    settings = {"allowed_workspaces": [], "lite_modules": []}
    modules = []
    reports = []
    doctypes = []
    pages = []
    MANIFEST_PATH = get_manifest_path()
    data_length = 0
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r") as f:
                data = json.load(f)
                if data: 
                    settings = data
                    data_length = len(data)
                    for mod, components in data.items():
                        modules.append(mod)
                        doctypes.extend(components.get("doctypes", []))
                        reports.extend(components.get("reports", []))
                        pages.extend(components.get("pages", []))
        except Exception:
            pass


    settings["lite_modules"] = frappe.get_all("Module Def", filters = {"name": ["not in", modules]}, pluck = "name")
    settings["locked_doctypes"] = doctypes
    settings["locked_reports"] = reports
    settings["locked_pages"] = pages
    settings["allowed_workspaces"] = frappe.get_all("Workspace", filters = {"name": ["in", ALLOWED_WORKSPACES]}, pluck="name")
    is_lite = 'LITE' if data_length > 0 else 'FULL'
    print(f"Initialization: Detected mode - {is_lite}")
    return {
        "workspaces": frappe.get_all("Workspace", pluck="name"),
        "modules": frappe.get_all("Module Def", pluck="name"),
        "settings": settings,
        "is_lite": is_lite
    }

@frappe.whitelist()
def save_settings(workspaces, modules):
    """Saves the user's UI selections to Global Defaults"""
    frappe.set_global_default("lite_allowed_workspaces", workspaces)
    frappe.set_global_default("lite_modules", modules)
    return "Settings Saved"
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
    """Provides a detailed scan of hidden vs visible components."""
    return {
        "hidden_workspaces": frappe.get_all("Workspace", filters={"is_hidden": 1}, pluck="name"),
        "readonly_doctypes": frappe.get_all("DocType", filters={"read_only": 1}, pluck="name"),
        "locked_modules": list(get_locked_manifest().get("modules", []))
    }

# Terminal Helper
def print_status():
    """Can be called via 'bench execute customized_forcommon.prunning.print_status'"""
    is_lite = bool(frappe.db.sql("SHOW TABLES LIKE 'tabLiteModeBackup'"))
    print(f"System Mode: {'LITE' if is_lite else 'FULL'}")
    summary = get_system_summary()
    print(f"Hidden Workspaces: {len(summary['hidden_workspaces'])}")
    print(f"Locked Modules: {len(summary['locked_modules'])}")
@frappe.whitelist()
def toggle_module_visibility_from_gui(module_name, hide):
    """Wrapper to ensure GUI calls are properly handled with whitelisting."""
    hide = bool(int(hide))  # Convert string '1'/'0' to boolean
    toggle_module_visibility(module_name, hide)