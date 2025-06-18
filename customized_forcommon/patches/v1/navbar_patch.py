import frappe

def execute():
    # Step 1: Delete unwanted items (optional)
    frappe.db.sql("""DELETE FROM `tabNavbar Item` WHERE parent = 'Navbar Settings'""")
    frappe.db.commit()

    # Step 2: Add custom standard items
    navbar_settings = frappe.get_single("Navbar Settings")

    navbar_settings.settings_dropdown = []
    navbar_settings.help_dropdown = []

    for item in get_standard_navbar_items():
        navbar_settings.append("settings_dropdown", item)

    for item in get_standard_help_items():
        navbar_settings.append("help_dropdown", item)

    navbar_settings.save(ignore_permissions=True)
    frappe.clear_cache()

def get_standard_navbar_items():
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
            "is_standard": 1,
            "item_label": "",
        },
        {
            "item_label": "Log out",
            "item_type": "Action",
            "action": "frappe.app.logout()",
            "is_standard": 1,
        },
    ]

def get_standard_help_items():
    return [
        {
            "item_label": "Keyboard Shortcuts",
            "item_type": "Action",
            "action": "frappe.ui.toolbar.show_shortcuts(event)",
            "is_standard": 1,
        },
    ]
