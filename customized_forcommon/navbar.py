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
