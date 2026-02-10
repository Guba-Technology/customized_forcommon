from frappe.core.doctype.user.user import User as BaseUser
import frappe

class CustomUser(BaseUser):
    def validate(self):
        # Exclude in setup wizard
        if frappe.flags.in_setup_wizard:
            return
        # Exclude Administrator
        if self.name == "Administrator":
            return

        super(CustomUser, self).validate()

        # This block is added for concat middle name also in the user full name
        parts = [self.first_name]
        if getattr(self, "middle_name", None):
            parts.append(self.middle_name)
        if getattr(self, "last_name", None):
            parts.append(self.last_name)
        self.full_name = " ".join(parts)


        # Only show warning if user has no assignment; don't forcibly disable here
        if not frappe.db.exists("User Company Assignment", {"user": self.name}):
            link = " ".join([
                f'<a href="/app/user-company-assignment/new?user={self.name}" style="text-decoration: underline" target=_blank >User Company Assignment</a>',
                'to assign the user to a company.'
            ])
            self.enabled = 0
            frappe.msgprint(
                f"User is not assigned to any company. Login will remain disabled. <br> Add Here {link}",
                indicator='orange'
            )

    def on_update(self):
        # Exclude Administrator
        if self.name == "Administrator":
            return

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
