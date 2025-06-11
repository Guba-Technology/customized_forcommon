app_name = "customized_forcommon"
app_title = "Customized Forcommon"
app_publisher = "Guba Technology"
app_description = "customizations for common operations"
app_email = "sewunet.abebaw@gubatech.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["erpnext"]
# email_brand_image = "assets/erpnext/images/erpnext-logo.jpg"
default_mail_footer = """
	<span>
		Sent via
		<a class="text-muted" href="https://gubatech.com?source=via_email_footer" target="_blank">
			ERP
		</a>
	</span>
"""

fixtures = [
    {
        "dt": "Workspace",
        "filters": [
            ["name", "in", ["Accounting", "HR", "Buying", "Selling",
                            "Manufacturing", "Stock", "Assets","ERPNext Settings","ERPNext Integrations","Integrations",
                            
                            "Employee Lifecycle","Recruitment","Leaves", "Procurement",
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
                          "Purchase Receipt", "Training Program", "Purchase Reciept",
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
                                         ]]    
        ]

    },

    {
        "dt": "Client Script",
        "filters":[
            ["dt", "in", ["Interview", "Purchase Invoice", "Employee Advance", "Payment Entry",
                          "BOM", "Quality Inspection", "Sales Order", "Material Request",

                          ]]
        ]
    }, 
    # Client Scripts using the name field
    # {
    #     "dt": "Client Script",
    #     "filters": [
    #         ["name", "in", [
    #             "Sales Invoice-Form",
    #             "Employee-Form",
    #             "Quality Inspection-Form"
    #         ]]
    #     ]
    # },

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
            ["name", "in", ["Job Card Status Report"]]
        ]
    },
    {
        "dt": "Property Setter",
        "filters": [
            ["name", "in", ["Workstation Type-workstation_type-Label", "Workstation-description-type", "Quality Inspection-status-reqd",
                            
                            
            ]]
        ]
    
    },

    ] 

#  this will be applied after the app is migrated
after_migrate = "customized_forcommon.patches.remove_job_card_summary.execute"


doc_events = {
    "Purchase Receipt": {
        "on_submit": "customized_forcommon.doc_events.purchase_receipt.update_stock_ledger_with_department",
    },
    "Item": {
        "autoname": "customized_forcommon.Item.custom_item_autoname",
        "on_update": "customized_forcommon.Item.custom_item_autoname"
    }
}


override_doctype_class = {
    "Employee": "customized_forcommon.overrides.employee.CustomEmployee",
    "Employee Promotion": "customized_forcommon.overrides.employee_promotion.CustomEmployeePromotion",
    "Employee Separation": "customized_forcommon.overrides.employee_separation.CustomEmployeeSeparation",
    "Material Request": "customized_forcommon.overrides.material_request.CustomMaterialRequest",
    "Sales Order": "customized_forcommon.overrides.sales_order.CustomSalesOrder",
    "Quality Inspection": "customized_forcommon.overrides.quality_inspection.CustomQualityInspection",
    
    
}

app_include_js = [
    "/assets/customized_forcommon/js/material_request.js"
]

# website_context = {
# 	"favicon": "/assets/one_fm/assets/images/ONEFM_Identity_Gray.png",
# 	"splash_image": "/assets/one_fm/assets/images/ONEFM_Identity_Gray.png",
# }
# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "customized_forcommon",
# 		"logo": "/assets/customized_forcommon/logo.png",
# 		"title": "Customized Forcommon",
# 		"route": "/customized_forcommon",
# 		"has_permission": "customized_forcommon.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/customized_forcommon/css/customized_forcommon.css"
# app_include_js = "/assets/customized_forcommon/js/customized_forcommon.js"

# include js, css files in header of web template
# web_include_css = "/assets/customized_forcommon/css/customized_forcommon.css"
# web_include_js = "/assets/customized_forcommon/js/customized_forcommon.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "customized_forcommon/public/scss/website"

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
override_doctype_class = {
    "Payment Request": "customized_forcommon.overrides.payment_request.CustomPaymentRequest",
    "Payment Entry": "customized_forcommon.overrides.payment_entry.CustomPaymentEntry",
}
# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "customized_forcommon/public/icons.svg"

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
# 	"methods": "customized_forcommon.utils.jinja_methods",
# 	"filters": "customized_forcommon.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "customized_forcommon.install.before_install"
# after_install = "customized_forcommon.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "customized_forcommon.uninstall.before_uninstall"
# after_uninstall = "customized_forcommon.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "customized_forcommon.utils.before_app_install"
# after_app_install = "customized_forcommon.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "customized_forcommon.utils.before_app_uninstall"
# after_app_uninstall = "customized_forcommon.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "customized_forcommon.notifications.get_notification_config"

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
# 		"customized_forcommon.tasks.all"
# 	],
# 	"daily": [
# 		"customized_forcommon.tasks.daily"
# 	],
# 	"hourly": [
# 		"customized_forcommon.tasks.hourly"
# 	],
# 	"weekly": [
# 		"customized_forcommon.tasks.weekly"
# 	],
# 	"monthly": [
# 		"customized_forcommon.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "customized_forcommon.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "customized_forcommon.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "customized_forcommon.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["customized_forcommon.utils.before_request"]
# after_request = ["customized_forcommon.utils.after_request"]

# Job Events
# ----------
# before_job = ["customized_forcommon.utils.before_job"]
# after_job = ["customized_forcommon.utils.after_job"]

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
# 	"customized_forcommon.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

