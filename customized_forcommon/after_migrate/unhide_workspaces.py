import frappe

def run():
    """After migrate: unhide all workspaces and clear cache."""
    print("🚀 Starting workspace unhide process...")

    unhide_all_workspaces()
    clear_workspace_cache()

    print("✅ All workspaces are now visible and cache cleared successfully.")


def unhide_all_workspaces():
    """Set is_hidden = 0 for all workspaces."""
    all_ws = frappe.get_all("Workspace", pluck="name")
    print(f"🔍 Found {len(all_ws)} total workspaces to unhide...")

    unhidden = 0

    for ws_name in all_ws:
        try:
            ws_doc = frappe.get_doc("Workspace", ws_name)
            if ws_doc.is_hidden:
                ws_doc.is_hidden = 0
                ws_doc.save(ignore_permissions=True)
                unhidden += 1
        except Exception as e:
            print(f"⚠️ Skipped workspace {ws_name}: {e}")

    frappe.db.commit()
    print(f"👁️ Unhidden {unhidden} workspaces successfully.")


def clear_workspace_cache():
    """Clear workspace cache so Desk sidebar refreshes immediately."""
    print("🧹 Clearing workspace cache and Redis keys...")

    frappe.clear_cache()
    frappe.cache().flushall()

    users = frappe.get_all("User", filters={"enabled": 1}, pluck="name")
    for user in users:
        for key in [
            f"desk_sidebar_{user}",
            f"workspace_sidebar_{user}",
            f"workspaces:{user}",
            f"bootinfo:{user}",
        ]:
            frappe.cache().delete_value(key)

    print("♻️ Workspace cache cleared for all users.")
