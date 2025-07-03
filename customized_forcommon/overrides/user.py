# customized_forcommon/custom_controllers/user_controller.py

# Import the base User controller class from Frappe's core
from frappe.core.doctype.user.user import User as BaseUser
import frappe

class CustomUser(BaseUser):
    """
    Custom controller for the User DocType.
    Overrides its behavior, specifically to ensure new users are disabled.
    """
    def validate(self):
        """
        Override the validate method. This runs for both new insertions and updates.
        """
        # IMPORTANT: Always call the parent's validate method first to run all standard validations.
        super(CustomUser, self).validate()

        # For new user creations (i.e., if doc.is_new() is True), ensure they are disabled.
        if self.is_new() and self.enabled:
            self.enabled = 0
            frappe.msgprint("New user created as disabled. Enable by assigning to a company via 'User Company Assignment'.",
                             indicator='orange')
        # check if the user is assigned to a company
        if not frappe.db.exists("User Company Assignment", {"user": self.name}):
            # If the user is not assigned to any company, disable the user.
            self.enabled = 0
            link = " ".join([
                f'<a href="/app/user-company-assignment/new?user={self.name}" style="text-decoration: underline" target=_blank >User Company Assignment</a>',
                'to assign the user to a company.'
            ])
            frappe.msgprint(f"User is not assigned to any company. User has been disabled. <br> Add Here {link}",
                             indicator='orange')