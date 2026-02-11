from frappe.core.doctype.user.user import User as BaseUser
import frappe

class CustomUser(BaseUser):
    def validate(self):
        """Validate before saving user."""
        # Skip validation during setup or for Administrator
        if frappe.flags.in_setup_wizard or self.name == "Administrator":
            return

        super(CustomUser, self).validate()

        # Concat full name
        parts = [self.first_name]
        if getattr(self, "middle_name", None):
            parts.append(self.middle_name)
        if getattr(self, "last_name", None):
            parts.append(self.last_name)
        self.full_name = " ".join(parts)

        # Check global user limit before enabling
        self.check_allowed_users()

    def check_allowed_users(self):
        """Enforce allowed users from site_config.json with dynamic messages."""
        allowed_users = frappe.local.conf.get('no_of_allowed_users')
        if not allowed_users:
            return  # No limit → skip

        # Count all currently enabled users
        active_users = frappe.db.count("User", {"enabled": 1})

        # Include this user if being enabled and not already counted
        if self.enabled:
            already_enabled = frappe.db.exists("User", {"name": self.name, "enabled": 1})
            if not already_enabled:
                active_users += 1

        # If exceeds allowed number, raise dynamic error
        if active_users > allowed_users:
            if self.is_new():  
                frappe.throw(
                    f"Cannot create a new user. Maximum allowed active users is <b>{allowed_users}</b>."
                )
            else:
                frappe.throw(
                    f"Cannot enable this user. Maximum allowed active users is <b>{allowed_users}</b>."
                )

    def on_update(self):
        """Recheck after update to ensure no violation."""
        if frappe.flags.in_setup_wizard or self.name == "Administrator":
            return

        super(CustomUser, self).on_update()

        # Recheck only if user is enabled
        if self.enabled:
            self.check_allowed_users()