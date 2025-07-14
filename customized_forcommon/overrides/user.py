from frappe.core.doctype.user.user import User as BaseUser
import frappe

class CustomUser(BaseUser):
    def validate(self):
        super(CustomUser, self).validate()

        # If new user, force disable
        if self.is_new() and self.enabled:
            self.enabled = 0

        # If no company assignment, disable user
        if not frappe.db.exists("User Company Assignment", {"user": self.name}):
            self.enabled = 0
            link = " ".join([
                f'<a href="/app/user-company-assignment/new?user={self.name}" style="text-decoration: underline" target=_blank >User Company Assignment</a>',
                'to assign the user to a company.'
            ])
            frappe.msgprint(
                f"User is not assigned to any company. User has been disabled. <br> Add Here {link}",
                indicator='orange'
            )

    def on_update(self):
        # After update, if disabled and user has company assignments, remove them
        if not self.enabled:
            assignments = frappe.get_all("User Company Assignment", filters={"user": self.name}, pluck="name")
            for assignment_name in assignments:
                frappe.delete_doc("User Company Assignment", assignment_name, ignore_permissions=True)
            if assignments and len(assignments) == 1:
                frappe.msgprint("User has been disabled. User has been removed from User Company Assignment.", indicator='red')
            elif assignments and len(assignments) > 1:
                frappe.msgprint("Users have been disabled. Users have been removed from all User Company Assignments.", indicator='red')
