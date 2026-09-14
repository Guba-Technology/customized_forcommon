from hrms.hr.doctype.appraisal.appraisal import Appraisal
from hrms.payroll.utils import sanitize_expression
import frappe
from frappe.utils import flt
class CustomAppraisal(Appraisal):
    def calculate_self_appraisal_score(self):
            total = 0
            meta = frappe.get_meta("Employee Feedback Rating")
            number_of_stars = meta.get_options("custom_score") or 5
            for entry in self.self_ratings:
                score = flt(entry.custom_score)
                total += flt(score)
    
            self.self_score = flt(total, self.precision("self_score"))
    def calculate_final_score(self):
            final_score = 0
            appraisal_cycle_doc = frappe.get_cached_doc("Appraisal Cycle", self.appraisal_cycle)
    
            formula = appraisal_cycle_doc.final_score_formula
            based_on_formula = appraisal_cycle_doc.calculate_final_score_based_on_formula
    
            if based_on_formula:
                employee_doc = frappe.get_cached_doc("Employee", self.employee)
                data = {
                    "goal_score": flt(self.goal_score_percentage),
                    "average_feedback_score": flt(self.avg_feedback_score),
                    "self_appraisal_score": flt(self.self_score),
                }
                data.update(appraisal_cycle_doc.as_dict())
                data.update(employee_doc.as_dict())
                data.update(self.as_dict())
    
                sanitized_formula = sanitize_expression(formula)
                final_score = frappe.safe_eval(sanitized_formula, data)
            else:
                final_score = (flt(self.goal_score_percentage) + flt(self.avg_feedback_score) + flt(self.self_score)) / 3
    
            self.final_score = flt(final_score, self.precision("final_score"))

    @frappe.whitelist()
    def set_kras_and_rating_criteria(self):
       
        if not self.appraisal_template:
            return

        self.set("appraisal_kra", [])
        self.set("self_ratings", [])
        self.set("goals", [])

        template = frappe.get_doc("Appraisal Template", self.appraisal_template)

        # Goals or KRAs
        for entry in template.goals:
            table_name = "goals" if self.rate_goals_manually else "appraisal_kra"
            self.append(table_name, {
                "kra": entry.key_result_area,
                "per_weightage": entry.per_weightage,
            })
        table = template.rating_criteria if template.custom_criteria_for == "Performance Feedback" else template.custom_self_appraisal_rating_criteria
        # Standard rating criteria
        for entry in table:
            self.append("self_ratings", {
                "criteria": entry.criteria,
                "per_weightage": entry.per_weightage,
            })

        # # Custom rating criteria
        # if hasattr(template, "custom_self_appraisal_rating_criteria") :
        #     for entry in template.custom_self_appraisal_rating_criteria:
        #         self.append("self_ratings", {
        #             "criteria": entry.criteria,
        #             "per_weightage": entry.per_weightage,
        #         })
        # else:
        #     print("Template has no custom_self_appraisal_rating_criteria field")

        # return self
