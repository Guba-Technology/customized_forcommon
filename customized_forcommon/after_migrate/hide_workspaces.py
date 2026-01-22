import frappe

# Whitelist of workspaces to keep visible
ALLOWED_WORKSPACES = [
    "Procurement",
    "Inventory",
    "Tools",
    "Home",
    "Accounting & Finance",
    "Financial Reports",
    "Payables",
    "Receivables",
    "Fixed Assets",
    "Sales and Marketing",
    "Users",
    "Manufacturing"
]

def run():
    """After migrate: hide all workspaces except those in ALLOWED_WORKSPACES and clear cache."""
    print("🚀 Starting workspace hide/unhide process...")

    hide_or_unhide_workspaces()
    clear_workspace_cache()

    print("✅ Workspace visibility updated and cache cleared successfully.")


def hide_or_unhide_workspaces():
    """Hide all workspaces except the whitelist and unhide whitelisted ones."""
    all_ws = frappe.get_all("Workspace", pluck="name")
    print(f"🔍 Found {len(all_ws)} total workspaces to process...")

    hidden_count = 0
    unhidden_count = 0

    for ws_name in all_ws:
        try:
            ws_doc = frappe.get_doc("Workspace", ws_name)

            if ws_name in ALLOWED_WORKSPACES and ws_doc.is_hidden:
                # Unhide whitelisted workspace
                ws_doc.is_hidden = 0
                ws_doc.save(ignore_permissions=True)
                unhidden_count += 1
            elif ws_name not in ALLOWED_WORKSPACES and not ws_doc.is_hidden:
                # Hide non-whitelisted workspace
                ws_doc.is_hidden = 1
                ws_doc.save(ignore_permissions=True)
                hidden_count += 1

        except Exception as e:
            print(f"⚠️ Skipped workspace {ws_name}: {e}")

    frappe.db.commit()
    print(f"👁️ Hidden {hidden_count} workspaces, Unhidden {unhidden_count} workspaces successfully.")


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
