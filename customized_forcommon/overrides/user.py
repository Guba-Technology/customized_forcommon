from frappe.core.doctype.user.user import User as BaseUser
import frappe

class CustomUser(BaseUser):
    def validate(self):
        """Validate before saving user."""
        # Skip validation during setup or for Administrator
        if frappe.flags.in_setup_wizard or self.name == "Administrator":
            return

        super(CustomUser, self).validate()

        # Check user count limit before enabling
        self.check_max_user_restriction()

    def check_max_user_restriction(self):
        """Ensure that enabling this user doesn't exceed company max user limit."""
        company = self.company  # Custom Link field to Company

        if not company:
            return  # Skip if no company assigned

        # Fetch limit for this company
        max_limit = frappe.db.get_value("Max User Restriction", {"company": company}, "no_of_users_allowed")
        if not max_limit:
            return  # No restriction record → skip

        # Count currently enabled users under same company
        active_users = frappe.db.count(
            "User",
            {"enabled": 1, "company": company}
        )

        # If user is being enabled and limit exceeded
        if self.enabled and active_users > max_limit:
            frappe.throw(
                f"Cannot enable user. "
                f"Maximum active users allowed for company <b>{company}</b> is {max_limit}. "
                f"Please disable another user first."
            )

    def on_update(self):
        """Triggered after user is updated."""
        if frappe.flags.in_setup_wizard or self.name == "Administrator":
            return

        super(CustomUser, self).on_update()

        company = self.company
        if not company:
            return

        # Recheck after update to ensure no violation
        if self.enabled:
            self.check_max_user_restriction()