# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ApplicantTestResult(Document):
	pass



@frappe.whitelist()
def get_applicant_test_scores(job_applicant):
    results = frappe.get_all(
        "Applicant Test Result",
        filters={"job_applicant": job_applicant},
        fields=["written_test_score", "practical_test_score"],
        ignore_permissions=True
    )
    return results
