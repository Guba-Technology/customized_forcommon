from frappe.core.doctype.user.user import User as BaseUser
import frappe

class CustomUser(BaseUser):
    def validate(self):
        super(CustomUser, self).validate()

        # Only show warning if user has no assignment; don't forcibly disable here
        if not frappe.db.exists("User Company Assignment", {"user": self.name}):
            link = " ".join([
                f'<a href="/app/user-company-assignment/new?user={self.name}" style="text-decoration: underline" target=_blank >User Company Assignment</a>',
                'to assign the user to a company.'
            ])
            frappe.msgprint(
                f"User is not assigned to any company. Login will remain disabled. <br> Add Here {link}",
                indicator='orange'
            )

    def on_update(self):
        super(CustomUser, self).on_update()
        # Clean-up: If the user is disabled, remove all their company assignments
        if not self.enabled:
            assignments = frappe.get_all(
                "User Company Assignment",
                filters={"user": self.name},
                pluck="name"
            )
            for assignment_name in assignments:
                frappe.delete_doc("User Company Assignment", assignment_name, ignore_permissions=True)
            if assignments:
                frappe.msgprint("User has been disabled and removed from all User Company Assignments.", indicator='red')
