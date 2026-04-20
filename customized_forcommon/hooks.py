app_name = "customized_forcommon"
app_title = "Customized Forcommon"
app_publisher = "Guba Technology"
app_description = "customizations for common operations"
app_email = "sewunet.abebaw@gubatech.com"
app_license = "mit"

# Required Apps
required_apps = ["erpnext", "hrms"]

# Branding
# Branding
email_brand_image = "/assets/customized_forcommon/images/gift.png"
default_mail_footer = """
	<span>
		Sent via
		<a class="text-muted" href="https://gubatech.com?source=via_email_footer" target="_blank">
			ERP
		</a>
	</span>
"""
website_context = {
	"favicon": "/assets/customized_forcommon/images/gift.png",
	"splash_image": "/assets/customized_forcommon/images/gift.png",
}

# Fixtures
fixtures = [
    {
        "dt": "Workspace",
        "filters": [
            ["name", "in", [
                "Accounting & Finance", "Human Resource", "Manufacturing","ERPNext Settings","ERPNext Integrations","Integrations",

                "Employee Lifecycle", "Recruitment", "Leaves", "Procurement",
                "Manufacturing", "Stock", "Fixed Assets", "Sales and Marketing",
                "Expense Claims", "Shift & Attendance", "Performance", "Users",
                "Payables",  "Receivables", "Financial Reports", "Expense Claim",
                "Salary Payout", "Tax & Benefits"

                            ]],
        ],
        "strict": False # do not check for existing records
    },


    {
        "dt": "Custom Field",
        "filters": [
            ["dt", "in", ["Employee", "Employee External Work History", "Employee Separation", "Interview",
                          "Asset", "Purchase Invoice", "Purchase Order", "Quotation", "Material Request",
                         "Company", "Employee Advance", "Sales Invoice", "Payment Entry", "Purchase Receipt", 
                         "Training Program", "Purchase Reciept", "Stock Entry", "Employee Internal Work History",
                          "Stock Ledger Entry", "Employee Grade", "Routing", "Training Event", "Leave Application",
                          "Training Result", "Travel Request", "Clearance", "Employee Grievance",  "Employee Incentive",
                          "Employee Promotion","Employee Transfer", "Employee Onboarding", "Appraisal Template", "Appraisal Template Goal",
                          "Employee Feedback Criteria", "KRA","Employee Feedback Rating", "Sales Order", "Customer", "Item", "Address", 
                          "Journal Entry",  "Additional Salary", "HR Settings","Employee Referral"
                        ]
            ],
        ]
    },
    {
        "dt": "Server Script",
        "filters": [
            ["reference_doctype", "in", [
                "Employee", "Employee External Work History", "Purchase Invoice", "Employee Lifecycle"
            ]]
        ]
    },
    {
        "dt": "Client Script",
        "filters":[
            ["dt", "in", ["Interview", "Purchase Invoice", "Employee Advance", "Payment Entry",
                          "Sales Invoice", "Employee",
                          "Sales Order", "Material Request", "Leave Application",

                          ]]
        ]
    },

    {
        "dt": "Print Format",
        "filters": [
            ["name", "in", [
                "Stock Entry Print Format", "Purchase Order Print Format", "Purchase Receipt Print Format",
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
                            "Employee-custom_leave_increment_period-Label", "Asset Movement-purpose-options", 
                            "Address-main-field_order", "Address-state-hidden", "Address-county-hidden", 
                            "Address-address_line1-description",
                            "Address-address_line2-description",
                            "Salary Structure-deductions-allow_on_submit",
                            "Salary Structure-earnings-allow_on_submit",
                            "Salary Structure-net_pay-allow_on_submit",
                            "Salary Structure-total_deduction-allow_on_submit",
                            "Salary Structure-total_earning-allow_on_submit",
                            "Stock Entry-add_to_transit-depends_on",
                            "Interview Round-expected_average_rating-hidden",
                            "Skill Assessment-rating-reqd",
                            "Skill Assessment-rating-in_list_view",
                            "Interview-expected_average_rating-hidden",
                            "Interview-average_rating-hidden",
                            "Sales Taxes and Charges-charge_type-options",
            ]]
        ]
    }
]


# Hooks
#  this will be applied after the app is migrated
after_migrate = [
    "customized_forcommon.after_migrate.rename_workspaces.run",
    "customized_forcommon.patches.remove_job_card_summary.execute",
    "customized_forcommon.after_migrate.clear_module_onboarding.clear_onboarding_docs"

]


# Doc Events that will be triggered on specific actions in the specified DocTypes
# For example, on_submit of Purchase Receipt will call the function update_stock_ledger_with_department
doc_events = {
    "Purchase Receipt": {
        "on_submit": "customized_forcommon.doc_events.purchase_receipt.update_stock_ledger_with_department"
    },
    "Item": {
        "autoname": "customized_forcommon.Item.custom_item_autoname",
        "on_update": "customized_forcommon.Item.custom_item_autoname",
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

    "KRA": {
        "before_insert": "customized_forcommon.doc_events.kra_hooks.auto_increment_kra_number"
    },

    "Customer": {
        "validate": "customized_forcommon.doc_events.customer.validate_license_dates"
    },
     "Batch": {
        "before_insert": "customized_forcommon.doc_events.batch_events.before_insert_batch",
    },
    "User": {
        "before_load": "customized_forcommon.doc_events.user_access_restriction.validate_user_access",
        "validate": "customized_forcommon.doc_events.user_access_restriction.validate_user_access"
    },
    "Journal Entry": {
        "on_submit": "customized_forcommon.doc_events.journal_entry.make_reversed"
    },
    "Company": {
        "on_update": "customized_forcommon.doc_events.company.update_employee_fuel_price"
    },
    "Employee": {
        "validate": ["customized_forcommon.doc_events.employee.update_fuel_payment",
                     "customized_forcommon.doc_events.employee.calculate_severance_amount"
        ]

    },
    "Employee Advance": {
        "validate": [
            "customized_forcommon.doc_events.employee_advance.validate_payment_type",
        ],
       
    },
      "Payment Entry": {
        "on_submit": [
            "customized_forcommon.doc_events.employee_advance.create_first_repayment_on_payment",
        ],
        "on_cancel": "customized_forcommon.doc_events.employee_advance.calculate_repayment_amount_during_payment_entry_cancellation"
    },

    "Additional Salary": {
        "on_submit": "customized_forcommon.doc_events.employee_advance.calculate_repayment_amount_during_additional_salary_submission",
        "on_cancel": "customized_forcommon.doc_events.employee_advance.calculate_repayment_amount_during_additional_salary_cancellation"
    },

    "Expense Claim": {
        "on_submit": "customized_forcommon.doc_events.employee_advance.calculate_repayment_amount_during_expense_claim",
        "on_cancel": "customized_forcommon.doc_events.employee_advance.calculate_repayment_amount_during_expense_claim"
    },
    "HR Settings": {
        "validate": "customized_forcommon.doc_events.hr_settings.validate_severance_starting_year",
        "on_update": "customized_forcommon.doc_events.hr_settings.update_employee_severance_pay_amount"

    },
    "Sales Invoice": {
        "validate": [
            "customized_forcommon.doc_events.tax_logic.calculate_total_factory_share",
            "customized_forcommon.doc_events.tax_logic.calculate_tax_amount_for_factory_share",
            "customized_forcommon.doc_events.tax_logic.calculate_tax_amount_for_sidf"
        ]
    },
    "Sales Order": {
        "validate": [
            "customized_forcommon.doc_events.tax_logic.calculate_total_factory_share",
            "customized_forcommon.doc_events.tax_logic.calculate_tax_amount_for_factory_share",
            "customized_forcommon.doc_events.tax_logic.calculate_tax_amount_for_sidf"
        ]
    },
    "POS Invoice": {
        "validate": [
            "customized_forcommon.doc_events.tax_logic.block_factory_share_and_sidf"
        ]
    },
    "Employee Referral": {
        "before_validate": "customized_forcommon.doc_events.employee_referal.handle_referral_fields",
        "onload": "customized_forcommon.doc_events.employee_referal.handle_referral_fields"
    }

}

permission_query_conditions = {
    "User": "customized_forcommon.doc_events.user_access_restriction.user_query_condition",
}

scheduler_events = {
    "hourly":
    [
        "customized_forcommon.scheduler.custom_next_leave_increment_year.execute",
    ],

     "daily":
    [
        "customized_forcommon.scheduler.customer_license_checker.execute",
        "customized_forcommon.scheduler.expired_items.mark_expired_batches",
        "customized_forcommon.scheduler.contract_notification.notify_expiring_contracts",
        "customized_forcommon.scheduler.employee_advance.process_repayments"
    ],

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
    "Appraisal": "customized_forcommon.overrides.appraisal.CustomAppraisal",
    "Employee Advance": "customized_forcommon.overrides.employee_advance.CustomEmployeeAdvance",
    "Customer": "customized_forcommon.overrides.customer.CustomCustomer",
    "Asset Movement": "customized_forcommon.overrides.asset_movement.CustomAssetMovement",
    "Attendance": "customized_forcommon.overrides.attendance.CustomAttendance",
    "Leave Encashment": "customized_forcommon.overrides.leave_encashment.CustomLeaveEncashment",
    "Employee Performance Feedback": "customized_forcommon.overrides.employee_performance_feedback.CustomEmployeePerformanceFeedback",
}

#Include JS only for specific doctypes
app_include_js = [
    # "/assets/customized_forcommon/js/material_request.js",
    "/assets/customized_forcommon/js/purchase_invoice.js",
    "/assets/customized_forcommon/js/whitelabel.js",
    "/assets/customized_forcommon/js/list_sidebar_override.js",
    "/assets/customized_forcommon/js/bom_creator_extended.js",
    "/assets/customized_forcommon/js/bank_reconciliation_statement.js",
    "/assets/customized_forcommon/js/purchase_analytics.js",
    "/assets/customized_forcommon/js/custom_purchase_order_analysis.js",
    "/assets/customized_forcommon/js/recruitment_analytics_patch.js",
    "/assets/customized_forcommon/js/employee_analytics_patch.js",

]

page_js = {
	"print": "public/js/print_override.js"
}
# web_include_js = [
# "/assets/customized_forcommon/js/redirect_apps.js"
# ]

website_redirects = [
    {"source": "/apps", "target": "/app/home"}
]

# js files to be included in the doctype views
doctype_js = {
    "Material Request": "public/js/material_request.js",
    "BOM Creator": "public/js/bom_creator_extended.js",
    "Staffing Plan": "public/js/staffing_plan.js",
    "Sales Invoice": "public/js/sales_invoice.js",
    "Purchase Invoice": "public/js/sales_invoice.js",
    "Travel Request": "public/js/travel_request.js",
    "Employee Grievance": "public/js/travel_request.js",
    "Training Result": "public/js/training_result.js",
    "Appraisal Template": "public/js/appraisal_template.js",
    "Appraisal":"public/js/appraisal.js",
    "Payment Entry": "public/js/payment_entry.js",
    "Asset":"public/js/asset.js",
    "Customer": "public/js/customer_type.js",
    "Item": "public/js/item.js",
    "Purchase Receipt": "public/js/purchase_reciept.js",
    "Asset Movement": "public/js/asset_movement.js",
    "Purchase Order": "public/js/purchase_order.js",
    "Material Request": "public/js/material_request.js",
    "Supplier Quotation": "public/js/supplier_quotation.js",
    "Quotation": "public/js/quotation.js",
    "Auto Repeat": "public/js/auto_repeat.js",
    "Stock Entry": "public/js/stock_entry.js",
    "Employee Advance": "public/js/employee_advance.js",
    "Employee Performance Feedback":"public/js/employee_performance_feedback.js",
    "Interview Round":"public/js/interview_round.js",
    "Interview Feedback":"public/js/interview_feedback.js",
    "Interview":"public/js/interview.js",
    "Employee Referral":"public/js/employee_referral_custom.js",
    "Training Program":"public/js/training_program_custom.js",
    "Training Event":"public/js/training_program_custom.js",

}
doctype_list_js = {
    "Asset": "public/js/asset_list.js",
    "Asset Borrowing": "public/js/assetborrow_list.js"
}

# this is used to override the get_leaves_for_period method in leave_application
# this is used to customize the leave balance calculation logic when half day leaves are used
import hrms.hr.doctype.leave_application.leave_application as leave_application_module
import customized_forcommon.overrides.leave_balance as custom_module

leave_application_module.get_leaves_for_period = custom_module.get_leaves_for_period

# Monkey Patching Recruitment Analytics
from hrms.hr.report.recruitment_analytics import recruitment_analytics
from hrms.hr.report.employee_analytics import employee_analytics
from customized_forcommon.utils.report_patche import custom_recruitment_analytics_execute
recruitment_analytics.execute = custom_recruitment_analytics_execute
#monkey Patching Employee Analytics
from customized_forcommon.utils.employee_analytics_patch import custom_employee_analytics_execute
employee_analytics.execute = custom_employee_analytics_execute

# Monkey Patch for employee advance
import hrms.hr.doctype.employee_advance.employee_advance as ea
from customized_forcommon.overrides.employee_advance import create_return_through_additional_salary

ea.create_return_through_additional_salary = create_return_through_additional_salary


jinja = {
    "methods": "customized_forcommon.utils.amharic_currency"
}


website_redirects = [
    {"source": "/apps", "target": "/app/home"}
]

# Extend the existing dashboard
override_doctype_dashboards = {
    "Purchase Order": "customized_forcommon.overrides.purchase_order_dashboard.get_data",
    "Stock Entry": "customized_forcommon.overrides.stock_entry_dashboard.get_data",
}

# migrations = [
#     "customization_manager.migrations.changing_fetch_from_attribute_of_advance_account_in_employee_advance"
# ]
# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "customized_forcommon",
# 		"logo": "/assets/customized_forcommon/logo.png",
# 		"title": "Blood Bank Customization",
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
# In your custom app's hooks.py
# override_whitelisted_methods = {
#     "hrms.hr.doctype.appraisal.appraisal.set_kras_and_rating_criteria": "customized_forcommon.overrides.appraisal.set_kras_and_rating_criteria"
# }

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
