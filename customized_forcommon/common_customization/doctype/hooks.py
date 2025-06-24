app_name = "customization_manager"
app_title = "Customization Manager"
app_publisher = "Guba Technologies"
app_description = "This app is used to customize apps, doctypes, and forms"
app_email = "info@guba.com"
app_license = "mit"
required_apps = ["erpnext","hrms"]
fixtures = [
    {
        "dt": "Workspace",
        "filters": [
            ["name", "in", ["Employee Lifecycle", "Recruitment", "Leaves", "Procurement",
                            "Manufacturing", "Stock", "Assets", "Sales and Marketing",
                            "Expense Claims", "Shift & Attendance", "Performance",
                            
                            ]],
        ],
        "strict": False # do not check for existing records
    }, 
    {
        "dt": "Custom Field",
        "filters": [
            ["dt", "in", ["Employee", "Employee External Work History", "Employee Separation", "Interview",
                          "Asset", "Purchase Invoice", "Purchase Order", "Quotation", "Material Request", 
                          "Workstation", "Company", "Employee Advance", "Sales Invoice", "Payment Entry",
                          "Purchase Receipt", "Leave Application", "Training Program", "Purchase Reciept",
                          "Stock Entry", "BOM Item", "Quality Inspection", "Employee Internal Work History",
                          "Stock Ledger Entry", "Employee Grade", "BOM Operation", "Workstation Type",
                          "Workstation", "Routing", "Quality Inspection Reading",
                          ]],
        ]
    },
    {
        "dt": "Server Script",
        "filters":[
            ["reference_doctype", "in", ["Employee", "Employee External Work History", "Purchase Invoice",
                                         "Leave Application", "Employee Lifecycle",
                                         ]]    
        ]

    },
    {
        "dt": "Client Script",
        "filters":[
            ["dt", "in", ["Interview", "Purchase Invoice", "Employee Advance", "Payment Entry",
                          "Sales Invoice", "Employee", "BOM", "Leave Application", "Quality Inspection",
                          "Sales Order", "Material Request",

                          ]]
        ]
    }, 
    {
        "dt": "Print Format", 
        "filters": [
            ["name", "in", ["Stock Entry Print Format", "Purchase Order Print Format", "Purchase Receipt Print Format",
                            "Quotation Print Format",]]
        ]
    },
    {
        "dt": "Workflow",
        "filters": [["name", "in", ["Preventive Maintenance Workflow", "Material Request workflow"]]]
    },
    {
        "dt": "Workflow State"
    },
    {
        "dt": "Workflow Action Master"
    },

    {
        "dt": "Report",
        "filters": [
            ["name", "in", ["Job Card Status Report", "Stock Ledger Report"]]
        ]
    },
    {
        "dt": "Property Setter",
        "filters": [
            ["name", "in", ["Workstation Type-workstation_type-Label", "Workstation-description-type", "Quality Inspection-status-reqd",
                            "Leave Application-half_day_date-label", "Leave Application-half_day_date-mandatory_depends_on",
            ]]
        ]

    }


]

#  this will be applied after the app is migrated
after_migrate = "customization_manager.patches.remove_job_card_summary.execute"


# in your custom app, in hooks.py

doc_events = {
    "Purchase Receipt": {
        "on_submit": "customization_manager.doc_events.purchase_receipt.update_stock_ledger_with_department",
    },
    "Item": {
        "autoname": "customization_manager.Item.custom_item_autoname",
        "on_update": "customization_manager.Item.custom_item_autoname"
    },
}

scheduler_events = {
    "daily": [
        "customization_manager.scheduler.leave_auto_extend.auto_extend_leave_allocations",
    ],

}

# patches = [
#     "customization_manager.patches.v1.update_field_option_for_employee_status"
# ]
override_doctype_class = {
    "Employee Onboarding": "customization_manager.overrides.employee_onboarding.CustomEmployeeOnboarding",
    "Gender": "customization_manager.overrides.gender.CustomGender",
    "Employee Group": "customization_manager.overrides.employee_group.CustomEmployeeGroup",
    "Payment Request": "customization_manager.overrides.payment_request.CustomPaymentRequest",
    "Employee": "customization_manager.overrides.employee.CustomEmployee",
    "Employee Promotion": "customization_manager.overrides.employee_promotion.CustomEmployeePromotion",
    "Employee Separation": "customization_manager.overrides.employee_separation.CustomEmployeeSeparation",
    "Payment Entry": "customization_manager.overrides.payment_entry.CustomPaymentEntry",
    "Material Request": "customization_manager.overrides.material_request.CustomMaterialRequest",
    "Sales Order": "customization_manager.overrides.sales_order.CustomSalesOrder",
    "Quality Inspection": "customization_manager.overrides.quality_inspection.CustomQualityInspection",
    
    
}

app_include_js = [
    "/assets/customization_manager/js/material_request.js"
]

# migrations = [
#     "customization_manager.migrations.changing_fetch_from_attribute_of_advance_account_in_employee_advance"
# ]
# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "customization_manager",
# 		"logo": "/assets/customization_manager/logo.png",
# 		"title": "Customization Manager",
# 		"route": "/customization_manager",
# 		"has_permission": "customization_manager.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/customization_manager/css/customization_manager.css"
# app_include_js = "/assets/customization_manager/js/customization_manager.js"

# include js, css files in header of web template
# web_include_css = "/assets/customization_manager/css/customization_manager.css"
# web_include_js = "/assets/customization_manager/js/customization_manager.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "customization_manager/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}


# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "customization_manager/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "customization_manager.utils.jinja_methods",
# 	"filters": "customization_manager.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "customization_manager.install.before_install"
# after_install = "customization_manager.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "customization_manager.uninstall.before_uninstall"
# after_uninstall = "customization_manager.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "customization_manager.utils.before_app_install"
# after_app_install = "customization_manager.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "customization_manager.utils.before_app_uninstall"
# after_app_uninstall = "customization_manager.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "customization_manager.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"customization_manager.tasks.all"
# 	],
# 	"daily": [
# 		"customization_manager.tasks.daily"
# 	],
# 	"hourly": [
# 		"customization_manager.tasks.hourly"
# 	],
# 	"weekly": [
# 		"customization_manager.tasks.weekly"
# 	],
# 	"monthly": [
# 		"customization_manager.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "customization_manager.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "customization_manager.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "customization_manager.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["customization_manager.utils.before_request"]
# after_request = ["customization_manager.utils.after_request"]

# Job Events
# ----------
# before_job = ["customization_manager.utils.before_job"]
# after_job = ["customization_manager.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"customization_manager.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

