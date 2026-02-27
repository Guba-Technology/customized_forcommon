from hrms.hr.doctype.appraisal.appraisal import Appraisal
import frappe

class CustomAppraisal(Appraisal):

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
