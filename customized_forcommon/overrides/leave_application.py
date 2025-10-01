# Import necessary modules from Frappe and ERPNext HR
from hrms.hr.doctype.leave_application.leave_application import LeaveApplication
from frappe.utils import getdate, cint
import frappe
from frappe import _
from datetime import timedelta

# Import the logger explicitly for info logging
from frappe.utils.logger import get_logger

# Initialize a logger for your custom app
# It's good practice to use __name__ or a specific name for your logger
logger = get_logger(__name__)


class CustomLeaveApplication(LeaveApplication):
    """
    Custom controller for the Leave Application DocType.
    This class overrides standard methods to implement custom logic for:
    1. Calculating total leave days, especially for half-day ranges (in validate()).
    2. Ensuring correct 'Half Day' status in automatically generated Attendance records
       by overriding the `update_attendance()` method, which is called during `on_submit()`.
    """

    def validate(self):
        """
        Overrides the standard validate method.
        This method runs *before* the document is saved or submitted.
        It calls the parent's validate method first, then applies custom leave day calculation.
        """
        super().validate()
        self.calculate_total_leave_days()

    def calculate_total_leave_days(self):
        """
        Calculate total leave days, ignoring holidays.
        If 'Half Day' is checked, take half of the total leave days.
        """
        if not self.from_date or not self.to_date:
            frappe.throw(_("From Date and To Date are required to calculate leave days."))

        from_date = getdate(self.from_date)
        to_date = getdate(self.to_date)

        # Get company's default holiday list
        holiday_list = frappe.get_value("Company", self.company, "default_holiday_list")
        holidays = []
        if holiday_list:
            holidays = frappe.get_all(
                "Holiday",
                filters={"parent": holiday_list},
                fields=["holiday_date"]
            )
            holidays = [getdate(h["holiday_date"]) for h in holidays]

        # Count non-holiday days in the range
        days_in_range = 0
        current_date = from_date
        while current_date <= to_date:
            if current_date not in holidays:
                days_in_range += 1
            current_date += timedelta(days=1)

        # Apply half-day logic to the total leave period
        self.total_leave_days = days_in_range * 0.5 if self.half_day else days_in_range


    def create_or_update_attendance(self, attendance_name, date):
        """
        Helper method to create a new Attendance record or update an existing one.
        The status of the attendance record is determined by the `self.half_day` flag.
        """
        # Determine the status based on the half_day flag
        status = "Half Day" if self.half_day else "On Leave" # Assuming "On Leave" for full days

        if attendance_name:
            # If an attendance record already exists, fetch and update it
            doc = frappe.get_doc("Attendance", attendance_name)
            doc.db_set({
                "status": status,
                "leave_type": self.leave_type,
                "leave_application": self.name
            })
            
        else:
            # If no attendance record exists, create a new one
            doc = frappe.new_doc("Attendance")
            doc.employee = self.employee
            doc.employee_name = self.employee_name
            doc.attendance_date = date
            doc.company = self.company
            doc.leave_type = self.leave_type
            doc.leave_application = self.name
            doc.status = status
            doc.flags.ignore_validate = True # Ignore validation for system-generated docs
            doc.insert(ignore_permissions=True) # Insert without permission checks
            doc.submit() # Submit the attendance record
            logger.info(
                f"Created new attendance for {self.employee} on {date} with status {status}.",
                "Custom Leave App Attendance Creation"
            )

    def update_attendance(self):
        """
        Overrides the standard `update_attendance` method of LeaveApplication.
        This method is called by the base class's `on_submit()` method.

        This custom implementation iterates through the leave period and calls
        `create_or_update_attendance` for each day, ensuring the correct
        'Half Day' or 'On Leave' status is applied to Attendance records.
        """
       
        from_date = getdate(self.from_date)
        to_date = getdate(self.to_date)

        current_date = from_date
        while current_date <= to_date:
            try:
                # Check if an attendance record for this employee and date already exists
                existing_attendance_name = frappe.db.get_value(
                    "Attendance",
                    {"employee": self.employee, "attendance_date": current_date},
                    "name"
                )

                # Call the helper method to create or update attendance for the current day
                self.create_or_update_attendance(existing_attendance_name, current_date)

            except Exception as e:
                # Log any errors encountered during attendance creation/update
                frappe.log_error(
                    f"Failed to create/update attendance for {self.employee} on {current_date}: {e}",
                    "Custom Leave App Attendance Error"
                )
                # Re-throw the error to indicate a problem during submission, if critical
                frappe.throw(_(f"Error processing attendance for {current_date}: {e}"))

            current_date += timedelta(days=1) # Move to the next day

        # IMPORTANT: We do NOT call super().update_attendance() here,
        # because we have fully replaced its behavior for both half-day and full-day
        # scenarios within this overridden method by calling our helper.
        # This ensures our custom logic is always used for attendance updates from this Leave Application.
