import frappe
from frappe.model.document import Document
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count

class UserCompanyAssignment(Document):
    def validate(self):
        self.check_user_assignment_to_company()

    def check_user_assignment_to_company(self):
        assigned_company = self.company
        assigned_user_id = self.user

        if not assigned_company or not assigned_user_id:
            frappe.throw("Both User and Company must be selected for the User Company Assignment.")

        # Exclude Administrator from restriction checks
        if assigned_user_id == "Administrator":
            return

        max_users_allowed = frappe.db.get_value(
            "Max User Restriction",
            {"company": assigned_company, "docstatus": 1},
            "no_of_users_allowed"
        )

        if not max_users_allowed:
            return

        UserCompanyAssignmentTable = DocType("User Company Assignment")
        UserTable = DocType("User")

        query = (
            frappe.qb.from_(UserCompanyAssignmentTable)
            .join(UserTable).on(UserCompanyAssignmentTable.user == UserTable.name)
            .where(UserCompanyAssignmentTable.company == assigned_company)
            .where(UserTable.enabled == 1)
        )

        if self.name:
            query = query.where(UserCompanyAssignmentTable.name != self.name)

        current_enabled_assigned_users_count = query.select(Count("*")).run()[0][0]
        projected_users_count = current_enabled_assigned_users_count + 1

        if projected_users_count > max_users_allowed:
            frappe.throw(
                f"Cannot assign user '{assigned_user_id}' to company '{assigned_company}'. "
                f"The maximum user limit of {max_users_allowed} for this company will be exceeded."
            )

    def on_update(self):
        assigned_user_id = self.user

        # Exclude Administrator from auto-enable logic
        if assigned_user_id == "Administrator":
            return

        if assigned_user_id:
            user_doc = frappe.get_doc("User", assigned_user_id)

            if not user_doc.enabled:
                user_doc.enabled = 1

            if user_doc.user_type != "System User":
                user_doc.user_type = "System User"

            user_doc.save(ignore_permissions=True)
            frappe.db.commit()

            frappe.msgprint(f"User '{user_doc.full_name}' has been enabled due to Company Assignment.")

    def on_trash(self):
        assigned_user_id = self.user

         # Exclude Administrator from auto-disable logic
        if assigned_user_id == "Administrator":
            frappe.msgprint("Administrator assignment deleted, but user remains enabled.", indicator="green")
            return

        if assigned_user_id:
            user_doc = frappe.get_doc("User", assigned_user_id)

            if user_doc.enabled:
                user_doc.enabled = 0
                user_doc.save(ignore_permissions=True)
                
                frappe.msgprint(f"User '{user_doc.full_name}' has been disabled due to Company Assignment deletion.")
