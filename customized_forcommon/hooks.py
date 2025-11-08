app_name = "customized_forcommon"
app_title = "Customized Forcommon"
app_publisher = "Guba Technology"
app_description = "customizations for common operations"
app_email = "sewunet.abebaw@gubatech.com"
app_license = "mit"

# Required Apps
required_apps = ["erpnext", "hrms"]

# Branding


# Fixtures
fixtures = [
    {
        "dt": "Workspace",
        "filters": [
            ["name", "in", [
                "Accounting & Finance", "Human Resource", "Buying", "Manufacturing","ERPNext Settings","ERPNext Integrations","Integrations",
                
                "Employee Lifecycle", "Recruitment", "Leaves", "Procurement",
                "Manufacturing", "Stock", "Fixed Assets", "Sales and Marketing",
                "Expense Claims", "Shift & Attendance", "Performance", "Users",
                "Payables",  "Receivables", "Financial Reports"
                            
                            ]],
        ],
        "strict": False # do not check for existing records
    }, 
    

    {
        "dt": "Custom Field",
        "filters": [
            ["dt", "in", ["Employee", "Employee External Work History", "Employee Separation", "Interview",
                          "Asset", "Purchase Invoice", "Purchase Order", "Quotation", "Material Request", 
                          "Company", "Employee Advance", "Sales Invoice", "Payment Entry",
                          "Purchase Receipt", "Training Program", "Purchase Reciept",
                          "Stock Entry", "Employee Internal Work History",
                          "Stock Ledger Entry", "Employee Grade", "BOM Operation",
                           "Routing",
                          "Training Event", "Leave Application"
                          ]],
        ]
    },
    {
        "dt": "Server Script",
        "filters": [
            ["reference_doctype", "in", [
                "Employee", "Employee External Work History", "Purchase Invoice", "Employee Lifecycle",
            ]]
        ]
    },
    {
        "dt": "Client Script",
        "filters":[
            ["dt", "in", ["Interview", "Purchase Invoice", "Employee Advance", "Payment Entry",
                          "Sales Invoice", "Employee", "Sales Order", "Material Request",
                           "Leave Application",
                          ]]
        ]
    }, 
    
    {
        "dt": "Print Format",
        "filters": [
            ["name", "in", [
                "Stock Entry Print Format",
                "Purchase Order Print Format",
                "Purchase Receipt Print Format",
                "Quotation Print Format"
            ]]
        ]
    },
    {
        "dt": "Workflow",

        "filters": [["name", "in", ["Stock Material Transfer"]]]

    },
    {"dt": "Workflow State"},
    {"dt": "Workflow Action Master"},
    {
        "dt": "Report",
        "filters": [
            ["name", "in", ["Job Card Status Report", "Stock Ledger Report"]]
        ]
    },
    {
        "dt": "Property Setter",
        "filters": [
            ["name", "in", ["Leave Application-main-mandatory_depends_on", "Training Event-section_break_18-depends_on", 
                            "Employee-custom_leave_increment_period-Label",         
                            
            ]]
        ]
    }
]
before_migrate = ["customized_forcommon.custom_report.my_utilities.module_creator.execute",
                  "customized_forcommon.patcher.execute",]


#  this will be applied after the app is migrated
after_migrate = [
    "customized_forcommon.after_migrate.rename_workspaces.run",
    "customized_forcommon.patches.remove_job_card_summary.execute"
]

# Doc Events that will be triggered on specific actions in the specified DocTypes
# For example, on_submit of Purchase Receipt will call the function update_stock_ledger_with_department
doc_events = {
    "Purchase Receipt": {
        "on_submit": "customized_forcommon.doc_events.purchase_receipt.update_stock_ledger_with_department",
    },
    "Item": {
        "autoname": "customized_forcommon.Item.custom_item_autoname",
        "on_update": "customized_forcommon.Item.custom_item_autoname"
    },
    "Interview": {
        "validate": "customized_forcommon.doc_events.interview_score.calculate_total_criteria_score",
    },
    "Leave Application": {
        "validate": "customized_forcommon.doc_events.set_leave_application_return_date.set_custom_return_date",
    },
    "Training Event":{
        "validate": "customized_forcommon.doc_events.traning_event_attendance.validate_training_event",
    },
    "Staffing Plan": {
        "validate": "customized_forcommon.doc_events.staffing_plan_custom.calculate_counts",
    },

   
}

scheduler_events = {
    "Hourly":
    [
        "customized_forcommon.scheduler.custom_next_leave_increment_year.execute",
    ]

}

override_doctype_class = {
    "Leave Application": "customized_forcommon.overrides.leave_application.CustomLeaveApplication",
    "User": "customized_forcommon.overrides.user.CustomUser",
    "Employee Onboarding": "customized_forcommon.overrides.employee_onboarding.CustomEmployeeOnboarding",
    "Gender": "customized_forcommon.overrides.gender.CustomGender",
    "Payment Request": "customized_forcommon.overrides.payment_request.CustomPaymentRequest",
    "Employee": "customized_forcommon.overrides.employee.CustomEmployee",
    "Employee Promotion": "customized_forcommon.overrides.employee_promotion.CustomEmployeePromotion",
    "Employee Separation": "customized_forcommon.overrides.employee_separation.CustomEmployeeSeparation",
    "Payment Entry": "customized_forcommon.overrides.wrapped_payment_entry.WrappedPaymentEntry",
    "Material Request": "customized_forcommon.overrides.material_request.CustomMaterialRequest",
    "Sales Order": "customized_forcommon.overrides.sales_order.CustomSalesOrder",
    "BOM Creator": "customized_forcommon.overrides.bom_creator.CustomBom", 
    "Stock Entry": "customized_forcommon.overrides.stock_entry.CustomStockEntry",
    "Employee Advance": "customized_forcommon.overrides.employee_advance.CustomEmployeeAdvance"
    
}

app_include_js = [
    "/assets/customized_forcommon/js/material_request.js",
    "/assets/customized_forcommon/js/purchase_invoice.js",
    "/assets/customized_forcommon/js/whitelabel.js",
    "/assets/customized_forcommon/js/list_sidebar_override.js",
    "/assets/customized_forcommon/js/bom_creator_extended.js"
]


# js files to be included in the doctype views
doctype_js = {
    # "BOM Creator": "public/js/bom_creator_extended.js",
    "Staffing Plan": "public/js/staffing_plan.js",
    "Sales Invoice": "public/js/sales_invoice.js",
    "Purchase Invoice": "public/js/sales_invoice.js",
    "Payment Entry": "public/js/payment_entry.js"
}


# this is used to override the get_leaves_for_period method in leave_application
# this is used to customize the leave balance calculation logic when half day leaves are used
import hrms.hr.doctype.leave_application.leave_application as leave_application_module
import customized_forcommon.overrides.leave_balance as custom_module
from customized_forcommon.overrides.custom_add_advance_gl_for_reference import custom_add_advance_gl_for_reference
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry
from customized_forcommon.overrides import custom_gl_entry
# Monkey patch the original PaymentEntry method
PaymentEntry.add_advance_gl_for_reference = custom_add_advance_gl_for_reference
leave_application_module.get_leaves_for_period = custom_module.get_leaves_for_period



jinja = {
    "methods": "customized_forcommon.utils.amharic_currency"
}


website_redirects = [
    {"source": "/apps", "target": "/app/home"}
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

