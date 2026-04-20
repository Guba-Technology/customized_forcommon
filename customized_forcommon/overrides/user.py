from frappe.core.doctype.user.user import User as BaseUser
import frappe


class CustomUser(BaseUser):
    EXCLUDED_USERS = ["Administrator", "Guest"]
    def validate(self):
        # Exclude in setup wizard
        if frappe.flags.in_setup_wizard:
            return
        # Exclude Administrator
        if self.name == "Administrator":
            return

        super(CustomUser, self).validate()

        # Skip if this is the last active user (excluding Administrator)
        if self._is_last_active_user():
            return

        # Only warn + disable if no company assignment exists
        if not frappe.db.exists("User Company Assignment", {"user": self.name}):

            link = (
                f'<a href="/app/user-company-assignment/new?user={self.name}" '
                f'style="text-decoration: underline" target="_blank">'
                f'User Company Assignment</a>'
            )

            self.enabled = 0

            frappe.msgprint(
                f"""
                User is not assigned to any company.<br>
                Login will remain disabled.<br><br>
                Add here: {link}
                """,
                indicator="orange"
            )

    def on_update(self):
        # Exclude Administrator
        if self.name == "Administrator":
            return

        super(CustomUser, self).on_update()

        # Cleanup assignments ONLY if user is disabled
        if not self.enabled:

            assignments = frappe.get_all(
                "User Company Assignment",
                filters={"user": self.name},
                pluck="name"
            )

            for assignment in assignments:
                frappe.delete_doc(
                    "User Company Assignment",
                    assignment,
                    ignore_permissions=True
                )

            if assignments:
                frappe.msgprint(
                    "User has been disabled and removed from all User Company Assignments.",
                    indicator="red"
                )

    def _is_last_active_user(self):
        """
        Prevent disabling the last enabled user (excluding Administrator)
        """

        active_users = frappe.db.count(
            "User",
            filters={
                "enabled": 1,
                "name": ["not in", self.EXCLUDED_USERS]
            }
        )

        # If only one active user exists → skip disabling
        return active_users <= 1
