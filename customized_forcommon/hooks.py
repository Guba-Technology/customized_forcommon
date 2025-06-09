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
    "Payment Request": "customization_manager.overrides.payment_request.CustomPaymentRequest",
    "Payment Entry": "customization_manager.overrides.payment_entry.CustomPaymentEntry",
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

