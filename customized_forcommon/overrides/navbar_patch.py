import frappe

def custom_add_standard_navbar_items():
    navbar_settings = frappe.get_single("Navbar Settings")

    # Always overwrite with your custom items
    navbar_settings.settings_dropdown = []
    navbar_settings.help_dropdown = []

    # Custom settings dropdown items
    navbar_settings.append("settings_dropdown", {
        "item_label": "My Profile",
        "item_type": "Route",
        "route": "/app/user-profile",
        "is_standard": 1,
    })

    navbar_settings.append("settings_dropdown", {
        "item_label": "Log out",
        "item_type": "Action",
        "action": "frappe.app.logout()",
        "is_standard": 1,
    })

    # Custom help dropdown items
    navbar_settings.append("help_dropdown", {
        "item_label": "About",
        "item_type": "Action",
        "action": "frappe.ui.toolbar.show_about()",
        "is_standard": 1,
    })

    navbar_settings.save(ignore_permissions=True)
