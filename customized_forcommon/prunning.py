"""
a utitlity file to prune the system to LITE mode by hiding unnecessary modules,
workspaces, doctypes and reports.
Also provides functions to restore full mode.
usage:
  from customized_forcommon.customized_forcommon import prunning
  prunning.run(mode="lite")  # to switch to LITE mode
  prunning.run(mode="full")  # to restore full mode
        Call the following functions on the UI  if needed:
        (PASS MODULE NAME AND hide=True/False PARAMETERS TO THESE FUNCTIONS)
        ---------------------------------------------------------------------
  prunning.toggle_module_visibility("Manufacturing", hide=True)  # to hide a specific module
  prunning.toggle_module_security("Manufacturing", hide=True)  # to lock access to a specific module


"""
import frappe
import json
from frappe.modules import reload_doc 

# asdd more qorkspace labels here if needed (name should be similar with workspace json file)
ALLOWED_WORKSPACES = [
    "Home", "Sales and Marketing", "Human Resource", "Inventory", "Purchase",
    "Accounting & Finance", "Users", "Settings"
]
# Modulees that are essential for LITE mode (module names from db- not from workspace)
LIT_MODULES = [
    "Accounts", "Stock", "Buying", "Selling", "HR", "Payroll", 
    "Setup", "Core", "Custom", "Desk", "Email", "Automation"
]
#  modules tobe hidn in LITE mode
HIDDEN_BY_DEFAULT = ["CRM", "Quality Management", "Quality", "Projects", "Assets", "Manufacturing"]

def run(mode="lite"):
    is_lite = (mode == "lite")
    print(f"Switching to {mode.upper()} mode...")
    
    try:
        if is_lite:
            apply_lite_mode()
        else:
            restore_full_mode()
            
        frappe.clear_cache()
        print(f" Successfully updated to {mode.upper()} mode.")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "LITE Mode Toggle Error")
        print(f" Error: {e}")

def apply_lite_mode():
    #hide workspacxes
    workspaces = frappe.get_all("Workspace", fields=["name", "module", "label"])
    allowed_dts = frappe.get_all("DocType", filters={"module": ["in", LIT_MODULES]}, pluck="name")

    for ws in workspaces:
        label = ws.label or ws.name
        is_hidden = 0 if label in ALLOWED_WORKSPACES else 1
        
        # Hide Sidebar Entry
        frappe.db.set_value("Workspace", ws.name, "is_hidden", is_hidden, update_modified=False)

        if not is_hidden:
            # remove from workspave links to prevent not founnd errors
            frappe.db.sql("""
                DELETE FROM `tabWorkspace Link` 
                WHERE parent = %s AND link_to NOT IN %s AND type != 'Card Break'
            """, (ws.name, tuple(allowed_dts + [""])))
            #and from the shortcuts too
            frappe.db.sql("""
                DELETE FROM `tabWorkspace Shortcut` 
                WHERE parent = %s AND link_to NOT IN %s
            """, (ws.name, tuple(allowed_dts + [""])))
            
            # Prune JSON content
            content = frappe.db.get_value("Workspace", ws.name, "content")
            if content:
                try:
                    data = json.loads(content)
                    clean_data = [
                        b for b in data if not (b.get("data", {}).get("link_to") or b.get("data", {}).get("shortcut_name")) 
                        or (b.get("data", {}).get("link_to") in allowed_dts) 
                        or (b.get("data", {}).get("shortcut_name") in allowed_dts)
                    ]
                    frappe.db.set_value("Workspace", ws.name, "content", json.dumps(clean_data), update_modified=False)
                except: pass
    
    toggle_metadata(True)

def restore_full_mode():
    print(" Unlocking Metadata (DocTypes, Modules, Reports)...")
    
    # make doct typees Searchable and Not Read-Only
    frappe.db.sql("""
        UPDATE `tabDocType` 
        SET read_only = 0, show_name_in_global_search = 1 
        WHERE custom = 0
    """)

    # Reset Module Def: Enable all modules
    if frappe.db.has_column("Module Def", "disabled"):
        frappe.db.sql("UPDATE `tabModule Def` SET disabled = 0")

    # eReset Reports: Enable all reports
    if frappe.db.has_column("Report", "disabled"):
        frappe.db.sql("UPDATE `tabReport` SET disabled = 0")

    print("Reloading Workspaces from source...")
    # Reset Workspaces
    workspaces = frappe.get_all("Workspace", fields=["name", "module"])

    for ws in workspaces:
        # Unhide
        frappe.db.set_value("Workspace", ws.name, "is_hidden", 0, update_modified=False)
        
        try:
            # oowner app
            app = frappe.db.get_value("Module Def", ws.module, "app_name")
            if app:
                reload_doc(frappe.scrub(app), "desktop_page", frappe.scrub(ws.name), force=True)
                print(f"Restored: {ws.name}")
        except Exception:
            #if not found, hidden always
            pass

    frappe.db.commit()
    print("Clearing Cache...")
    frappe.clear_cache()

def toggle_metadata(is_lite):
    # make visibility affected
    status = 1 if is_lite else 0
    search = 0 if is_lite else 1
    
    # for DocTypes
    frappe.db.sql("""
        UPDATE `tabDocType` SET read_only = %s, show_name_in_global_search = %s
        WHERE (module IN %s OR (module NOT IN %s AND %s = 1)) AND custom = 0
    """, (status, search, tuple(HIDDEN_BY_DEFAULT), tuple(LIT_MODULES), status))

    # for Module Def
    if frappe.db.has_column("Module Def", "disabled"):
        frappe.db.sql("""
            UPDATE `tabModule Def` SET disabled = %s 
            WHERE (name IN %s OR (name NOT IN %s AND %s = 1))
        """, (status, tuple(HIDDEN_BY_DEFAULT), tuple(LIT_MODULES), status))
    
    frappe.db.commit()

def toggle_module_visibility(module_name, hide=True):
    
    print(f"{' Hiding' if hide else ' Restoring'} everything related to module: {module_name}...")

    status = 1 if hide else 0
    search = 0 if hide else 1

    # 1hide/show Module Def itself
    if frappe.db.has_column("Module Def", "disabled"):
        frappe.db.set_value("Module Def", module_name, "disabled", status)

    # hide/show DocTypes in this module
    frappe.db.sql("""
        UPDATE `tabDocType` 
        SET read_only = %s, show_name_in_global_search = %s 
        WHERE module = %s AND custom = 0
    """, (status, search, module_name))
    # hide/show Reports in this module
    if frappe.db.has_column("Report", "disabled"):
        frappe.db.sql("UPDATE `tabReport` SET disabled = %s WHERE module = %s", (status, module_name))

    # hide/show Workspaces associated with this module
    workspaces = frappe.get_all("Workspace", filters={"module": module_name}, fields=["name"])
    
    for ws in workspaces:
        if hide:
            frappe.db.set_value("Workspace", ws.name, "is_hidden", 1, update_modified=False)
        else:
            # Full Restore: Reload from JSON source if it exists
            frappe.db.set_value("Workspace", ws.name, "is_hidden", 0, update_modified=False)
            try:
                app = frappe.db.get_value("Module Def", module_name, "app_name")
                if app:
                    reload_doc(frappe.scrub(app), "desktop_page", frappe.scrub(ws.name), force=True)
            except:
                pass

    frappe.db.commit()
    frappe.clear_cache()
    print(f" Module '{module_name}' has been {'hidden' if hide else 'restored'}.")

def toggle_module_security(module_name, hide=True):

    print(f"{'Locking' if hide else ' Unlocking'} access to module: {module_name}...")

    toggle_module_visibility(module_name, hide=hide)

    doctypes = frappe.get_all("DocType", filters={"module": module_name, "custom": 0}, pluck="name")

    if hide:
        lock_permissions(doctypes)
    else:
        unlock_permissions(doctypes)

    frappe.clear_cache()
    print(f"Security policy applied to {module_name}.")

def lock_permissions(doctypes):
    if not doctypes: return
    
    print(f"Locking permissions for {len(doctypes)} DocTypes...")
    
    for dt_name in doctypes:
        frappe.db.sql("""
            UPDATE `tabDocPerm` 
            SET `read` = 0, `write` = 0, `create` = 0, `delete` = 0, 
                `submit` = 0, `cancel` = 0, `amend` = 0 
            WHERE parent = %s
        """, (dt_name,))
        
    frappe.db.commit()
    print(f"Access blocked for all roles on specified DocTypes.")

def unlock_permissions(doctypes):
    if not doctypes: return
    
    print(f"  Restoring permissions...")
    for dt in doctypes:
        try:
            module_name = frappe.db.get_value("DocType", dt, "module")
            app_name = frappe.db.get_value("Module Def", module_name, "app_name") or "erpnext"
            
          
            reload_doc(app_name, "doctype", frappe.scrub(dt), force=True)
            print(f"    ✔ Source Reload: {dt}")
            
        except Exception:
           
            frappe.db.sql("""
                UPDATE `tabDocPerm` 
                SET `read` = 1, `write` = 1, `create` = 1, `export` = 1
                WHERE parent = %s AND role IN ('System Manager', 'Administrator', 'Sales Manager', 'Sales User')
            """, (dt,))
            print(f"    ✔ DB Reset: {dt} (Used SQL Fallback)")

    frappe.db.commit()

def rebuild_search_index(doctypes):
    """Forces the search index to update for the restored DocTypes."""
    from frappe.utils.global_search import rebuild_for_doctype
    print(" Rebuilding search index for restored items...")
    for dt in doctypes:
        try:
            rebuild_for_doctype(dt)
        except:
            pass
def toggle_module_visibility(module_name, hide=True):
    status = 1 if hide else 0
    search = 0 if hide else 1
    
    if frappe.db.has_column("Module Def", "disabled"):
        frappe.db.set_value("Module Def", module_name, "disabled", status)

    frappe.db.sql("UPDATE `tabDocType` SET read_only=%s, show_name_in_global_search=%s WHERE module=%s", 
                  (status, search, module_name))

    frappe.db.sql("UPDATE `tabWorkspace` SET is_hidden=%s WHERE module=%s", (status, module_name))
    frappe.db.commit()