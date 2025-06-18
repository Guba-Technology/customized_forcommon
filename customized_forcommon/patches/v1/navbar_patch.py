import frappe

def execute():
    """Reset and configure the standard Navbar items (Settings & Help) for all users."""
    try:
        navbar_settings = frappe.get_single("Navbar Settings")

        # Step 1: Clear existing dropdowns (safe way without delete validation errors)
        navbar_settings.set("settings_dropdown", [])
        navbar_settings.set("help_dropdown", [])

        # Step 2: Append standard custom items
        for item in get_standard_navbar_items():
            navbar_settings.append("settings_dropdown", item)

        for item in get_standard_help_items():
            navbar_settings.append("help_dropdown", item)

        # Step 3: Save and refresh cache
        navbar_settings.save(ignore_permissions=True)
        frappe.clear_cache()

        frappe.msgprint("Navbar settings updated successfully.")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Navbar Setup Failed")
        frappe.throw("Failed to set up Navbar Settings. See error log.")

def get_standard_navbar_items():
    """Return list of standard settings items for the Navbar."""
    return [
        {
            "item_label": "My Profile",
            "item_type": "Route",
            "route": "/app/user-profile",
            "is_standard": 1,
        },
        {
            "item_label": "My Settings",
            "item_type": "Action",
            "action": "frappe.ui.toolbar.route_to_user()",
            "is_standard": 1,
        },
        {
            "item_label": "Session Defaults",
            "item_type": "Action",
            "action": "frappe.ui.toolbar.setup_session_defaults()",
            "is_standard": 1,
        },
        {
            "item_label": "Reload",
            "item_type": "Action",
            "action": "frappe.ui.toolbar.clear_cache()",
            "is_standard": 1,
        },
        {
            "item_label": "View Website",
            "item_type": "Action",
            "action": "frappe.ui.toolbar.view_website()",
            "is_standard": 1,
        },
        {
            "item_label": "Toggle Full Width",
            "item_type": "Action",
            "action": "frappe.ui.toolbar.toggle_full_width()",
            "is_standard": 1,
        },
        {
            "item_type": "Separator",
            "item_label": "",
            "is_standard": 1,
        },
        {
            "item_label": "Log out",
            "item_type": "Action",
            "action": "frappe.app.logout()",
            "is_standard": 1,
        },
    ]

def get_standard_help_items():
    """Return list of standard help items for the Navbar."""
    return [
        {
            "item_label": "Keyboard Shortcuts",
            "item_type": "Action",
            "action": "frappe.ui.toolbar.show_shortcuts(event)",
            "is_standard": 1,
        },
    ]
