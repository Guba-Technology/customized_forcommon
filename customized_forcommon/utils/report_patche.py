import frappe
from frappe import _
from hrms.hr.report.recruitment_analytics.recruitment_analytics import execute as original_execute

def custom_recruitment_analytics_execute(filters=None):
    columns, data = original_execute(filters)

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