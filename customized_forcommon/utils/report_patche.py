import frappe
from frappe import _
from hrms.hr.report.recruitment_analytics.recruitment_analytics import execute as original_execute

def custom_recruitment_analytics_execute(filters=None):
    if not filters:
        filters = frappe._dict({})
    else:
        filters = frappe._dict(filters)

    if filters.from_date:
        filters.on_date = filters.from_date
    elif filters.to_date:
        filters.on_date = filters.to_date

    columns, data = original_execute(filters)

    if filters.from_date and filters.to_date:
        valid_plans = frappe.get_all("Staffing Plan", filters={
            "company": filters.company,
            "from_date": [">=", filters.from_date],
            "to_date": ["<=", filters.to_date]
        }, pluck="name")
        
        data = [row for row in data if row.get("staffing_plan") in valid_plans]

    columns.extend([
        {"label": _("Written Score"), "fieldname": "written_test_score", "fieldtype": "Float", "width": 100},
        {"label": _("Practical Score"), "fieldname": "practical_test_score", "fieldtype": "Float", "width": 100}
    ])

    applicant_ids = [row.get("job_applicant") for row in data if row.get("job_applicant")]

    if applicant_ids:
        test_results = frappe.get_all("Applicant Test Result",
            filters={"job_applicant": ["in", applicant_ids]},
            fields=["job_applicant", "written_test_score", "practical_test_score"]
        )

        score_map = {res.job_applicant: res for res in test_results}

        for row in data:
            ja_id = row.get("job_applicant")
            if ja_id in score_map:
                row["written_test_score"] = score_map[ja_id].written_test_score
                row["practical_test_score"] = score_map[ja_id].practical_test_score

    return columns, data