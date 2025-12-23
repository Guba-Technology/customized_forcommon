import frappe
def run():
    """After migrate: after rename workspaces, hide others using is_hidden, and clear cache."""
    print("🚀 Starting workspace rename and restriction process...")

    hide_unallowed_workspaces()
    clear_workspace_cache()

def hide_unallowed_workspaces():
    """Hide all workspaces except allowed ones using the is_hidden field."""
    allowed = ["Home", "Sales and Marketing", "Human Resource", "Inventory", "Purchase",
               "Employee Lifecycle", "Recruitment", "Leaves", "Expense Claims", "Shift & Attendance",
                "Performance", "Users", "Accounting & Finance", "Payables",  "Receivables", "Financial Reports"
                ]
    all_ws = frappe.get_all("Workspace", pluck="name")
    print(f"🔍 Found {len(all_ws)} total workspaces in the system...")

    hidden_count = 0
    shown_count = 0

    for ws_name in all_ws:
        try:
            ws_doc = frappe.get_doc("Workspace", ws_name)
            label = ws_doc.label or ws_doc.name

            ws_doc.is_hidden = 0 if label in allowed else 1
            clean_broken_links(ws_doc)
            ws_doc.save(ignore_permissions=True)

            if ws_doc.is_hidden:
                hidden_count += 1
            else:
                shown_count += 1
        except Exception as e:
            print(f"⚠️ Skipped workspace {ws_name}: {e}")

    frappe.db.commit()
    print(f"🙈 Hidden {hidden_count} workspaces, kept {shown_count} visible.")
    print("✅ Workspace visibility updated (using is_hidden field).")


def clean_broken_links(ws_doc):
    """Remove invalid linked doctypes to prevent validation errors."""
    for field in ["shortcuts", "links", "charts", "quick_lists"]:
        if not ws_doc.get(field):
            continue
        valid_rows = []
        for row in ws_doc.get(field):
            try:
                if row.link_to and not frappe.db.exists("DocType", row.link_to):
                    continue
                valid_rows.append(row)
            except Exception:
                continue
        ws_doc.set(field, valid_rows)


# ---------------------------------------------------------------------------
# 3️⃣ Clear Workspace Cache
# ---------------------------------------------------------------------------
def clear_workspace_cache():
    """Clear workspace cache so the Desk sidebar refreshes immediately."""
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
