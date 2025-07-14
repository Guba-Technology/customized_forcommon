import frappe
from frappe.model.document import Document

def calculate_total_criteria_score(doc, method):
    if doc.custom_criteria_score:
        total_score = 0
        for criteria in doc.custom_criteria_score:
            total_score += criteria.get("score", 0)
        doc.custom_total_criteria_score = total_score
