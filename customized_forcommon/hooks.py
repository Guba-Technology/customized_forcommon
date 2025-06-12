app_name = "customized_forcommon"
app_title = "Customized Forcommon"
app_publisher = "Guba Technology"
app_description = "customizations for common operations"
app_email = "sewunet.abebaw@gubatech.com"
app_license = "mit"

# Required Apps
required_apps = ["erpnext", "hrms"]

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
                "Accounting", "HR", "Buying", "Selling", "Manufacturing", "ERPNext Settings", "ERPNext Integrations",
                "Integrations", "Employee Lifecycle", "Recruitment", "Leaves", "Procurement", "Stock", "Assets",
                "Sales and Marketing", "Expense Claims", "Shift & Attendance", "Performance",
            ]],
        ],
        "strict": False
    },
    {
        "dt": "Custom Field",
        "filters": [
            ["dt", "in", [
                "Employee", "Employee External Work History", "Employee Separation", "Interview", "Asset", "Purchase Invoice",
                "Purchase Order", "Quotation", "Material Request", "Workstation", "Company", "Employee Advance",
                "Sales Invoice", "Payment Entry", "Purchase Receipt", "Training Program", "Purchase Reciept",
                "Stock Entry", "BOM Item", "Quality Inspection", "Employee Internal Work History",
                "Stock Ledger Entry", "Employee Grade", "BOM Operation", "Workstation Type",
                "Workstation", "Routing", "Quality Inspection Reading",
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
        "filters": [
            ["dt", "in", [
                "Interview", "Purchase Invoice", "Employee Advance", "Payment Entry",
                "Sales Invoice", "Employee", "BOM", "Quality Inspection",
                "Sales Order", "Material Request",
            ]]
        ]
    },
    {
        "dt": "Print Format",
        "filters": [
            ["name", "in", [
                "Stock Entry Print Format", "Purchase Order Print Format", "Purchase Receipt Print Format",
                "Quotation Print Format",
            ]]
        ]
    },
    {
        "dt": "Workflow",
        "filters": [
            ["name", "in", ["Preventive Maintenance Workflow", "Material Request workflow"]]
        ]
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
            ["name", "in", [
                "Workstation Type-workstation_type-Label",
                "Workstation-description-type",
                "Quality Inspection-status-reqd",
            ]]
        ]
    }
]

# Hooks
after_migrate = "customized_forcommon.patches.remove_job_card_summary.execute"

doc_events = {
    "Purchase Receipt": {
        "on_submit": "customized_forcommon.doc_events.purchase_receipt.update_stock_ledger_with_department",
    },
    "Item": {
        "autoname": "customized_forcommon.Item.custom_item_autoname",
        "on_update": "customized_forcommon.Item.custom_item_autoname",
    }
}

scheduler_events = {
    "daily": [
        "customized_forcommon.scheduler.leave_auto_extend.auto_extend_leave_allocations",
    ]
}

override_doctype_class = {
    "Payment Request": "customized_forcommon.overrides.payment_request.CustomPaymentRequest",
    "Employee": "customized_forcommon.overrides.employee.CustomEmployee",
    "Employee Promotion": "customized_forcommon.overrides.employee_promotion.CustomEmployeePromotion",
    "Employee Separation": "customized_forcommon.overrides.employee_separation.CustomEmployeeSeparation",
    "Payment Entry": "customized_forcommon.overrides.payment_entry.CustomPaymentEntry",
    "Material Request": "customized_forcommon.overrides.material_request.CustomMaterialRequest",
    "Sales Order": "customized_forcommon.overrides.sales_order.CustomSalesOrder",
    "Quality Inspection": "customized_forcommon.overrides.quality_inspection.CustomQualityInspection",
}

app_include_js = [
    "/assets/customized_forcommon/js/material_request.js"
]
