import frappe
from frappe.utils import cint, flt
from customization_manager.api import get_designation_counts  # import your method

def calculate_counts(doc, method):
    doc.total_estimated_budget = 0

    for row in doc.staffing_details:
        counts = get_designation_counts(
            designation=row.designation,
            company=doc.company,
            department=doc.department  # from parent
        )
        row.current_count = counts["employee_count"]
        row.current_openings = counts["job_openings"]
        row.number_of_positions = cint(row.vacancies) + cint(row.current_count)

        if row.vacancies and row.estimated_cost_per_position:
            row.total_estimated_cost = cint(row.vacancies) * flt(row.estimated_cost_per_position)
        else:
            row.total_estimated_cost = 0

        doc.total_estimated_budget += row.total_estimated_cost
