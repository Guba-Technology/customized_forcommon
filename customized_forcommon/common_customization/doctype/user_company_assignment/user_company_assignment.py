# Copyright (c) 2025, Guba Technology and contributors
# For license information, please see license.txt

# Path: ~/frappe-bench/apps/customized_forcommon/customized_forcommon/custom_controllers/user_company_assignment_controller.py

import frappe
from frappe.model.document import Document
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count

class UserCompanyAssignment(Document):
    def validate(self):
        """
        This method is called before any save operation (insert or update) for a User Company Assignment document.
        It implements the maximum user limit per company.
        """
        self.check_user_assignment_to_company()
    
    def check_user_assignment_to_company(self):
        """
        Contains the logic to check if assigning a user to a company would exceed the allowed limit.
        """
        assigned_company = self.company
        assigned_user_id = self.user

        if not assigned_company or not assigned_user_id:
            frappe.throw("Both User and Company must be selected for the User Company Assignment.")
            return

        # Get the maximum allowed users for this company from Max User Restriction DocType.
        # Added docstatus=1 to ensure we only check against active restrictions.
        max_users_allowed = frappe.db.get_value(
            "Max User Restriction",
            {"company": assigned_company, "docstatus": 1},
            "no_of_users_allowed" # Ensure this matches your field name in Max User Restriction
        )

        if not max_users_allowed:
            return
        
        # --- Using Frappe Query Builder (frappe.qb) for robust counting ---
        UserCompanyAssignmentTable = DocType("User Company Assignment")
        UserTable = DocType("User")

        # Start building the query to count existing enabled users assigned to this company.
        query = (
            frappe.qb.from_(UserCompanyAssignmentTable)
            .join(UserTable)
            .on(UserCompanyAssignmentTable.user == UserTable.name)
            .where(UserCompanyAssignmentTable.company == assigned_company)
            .where(UserTable.enabled == 1) # Only count already enabled users
        )

        # If the current 'User Company Assignment' record exists (i.e., it's an update),
        # exclude it from the count to avoid incorrect double-counting.
        if self.name: # self.name is set for existing documents
            query = query.where(UserCompanyAssignmentTable.name != self.name)

        # Execute the query to get the count
        current_enabled_assigned_users_count = query.select(Count("*")).run()[0][0]

        # --- End of Frappe Query Builder section ---

        # Calculate the projected count *after* this assignment is saved and enables the user.
        # We assume this current user, if assigned, will become an enabled user.
        projected_users_count = current_enabled_assigned_users_count + 1

        # Check if the projected count exceeds the maximum allowed.
        if projected_users_count > max_users_allowed:
            frappe.throw(
                f"Cannot assign user '{assigned_user_id}' to company '{assigned_company}'. "
                f"The maximum user limit of {max_users_allowed} for this company will be exceeded."
            )

    def on_update(self):
        """
        This method is called after a document is inserted or updated.
        It handles enabling the linked system user.
        """
        assigned_user_id = self.user

        if assigned_user_id:
            user_doc = frappe.get_doc("User", assigned_user_id)

            # Only enable if the user is not already enabled.
            if not user_doc.enabled:
                user_doc.enabled = 1
                user_doc.user_type = "System User"  # Ensure the user type is set correctly.
                # Save with ignore_permissions=True to ensure it works even if the script context
                # doesn't have direct write permissions to the User DocType.
                user_doc.save(ignore_permissions=True)
                link = " ".join([
                    f'<a href="/app/user/{user_doc.email}" style="text-decoration: underline" >{user_doc.full_name}</a>',
                    'to assign the user to a company.'
                ])
                frappe.msgprint(f"User '{link}' has been enabled due to Company Assignment.")
    def on_trash(self):
        """
        This method is called when a document is deleted.
        It handles disabling the linked system user.
        """
        assigned_user_id = self.user

        if assigned_user_id:
            user_doc = frappe.get_doc("User", assigned_user_id)

            # Only disable if the user is currently enabled.
            if user_doc.enabled:
                user_doc.enabled = 0
                user_doc.save(ignore_permissions=True)
                frappe.msgprint(f"User '{user_doc.full_name}' has been disabled due to Company Assignment deletion.")