import frappe

def run():
    """After migrate: rename workspaces, hide/unhide based on allowed list, and clear cache."""
    print("🚀 Starting workspace visibility update process...")
    hide_unallowed_workspaces()
    clear_workspace_cache()

def hide_unallowed_workspaces():
    """Hide all workspaces except allowed ones using is_hidden field."""
    allowed = [
        "Home", "Sales and Marketing", "Human Resource", "Inventory", "Purchase",
        "Employee Lifecycle", "Recruitment", "Leaves", "Expense Claims", "Shift & Attendance",
        "Performance", "Users", "Accounting & Finance", "Payables", "Receivables",
        "Financial Reports", "Payroll", "Salary Payout", "Tax & Benefits"
    ]

    all_ws = frappe.get_all("Workspace", ["name", "label", "is_hidden"])
    print(f"🔍 Found {len(all_ws)} total workspaces in the system...")

    hidden_count, shown_count = 0, 0

    for ws in all_ws:
        label = ws.label or ws.name
        should_hide = 0 if label in allowed else 1

        # Only update if different to avoid unnecessary saves
        if ws.is_hidden != should_hide:
            try:
                frappe.db.set_value("Workspace", ws.name, "is_hidden", should_hide, update_modified=False)
                if should_hide:
                    hidden_count += 1
                else:
                    shown_count += 1
            except Exception as e:
                print(f"⚠️ Failed to update {ws.name}: {e}")

    frappe.db.commit()
    print(f"🙈 Hidden {hidden_count} workspaces, unhidden {shown_count}.")
    print("✅ Workspace visibility updated successfully.")

def clear_workspace_cache():
    """Clear workspace cache so the Desk sidebar refreshes immediately."""
    print("🧹 Clearing workspace cache and Redis keys...")

    frappe.clear_cache()
    cache = frappe.cache()
    cache.flushall()

    users = frappe.get_all("User", filters={"enabled": 1}, pluck="name")
    for user in users:
        for key in [
            f"desk_sidebar_{user}",
            f"workspace_sidebar_{user}",
            f"workspaces:{user}",
            f"bootinfo:{user}",
        ]:
            cache.delete_value(key)

    print("♻️ Workspace cache cleared for all users.")
