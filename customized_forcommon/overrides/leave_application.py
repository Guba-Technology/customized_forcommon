# Import necessary modules from Frappe and ERPNext HR
from hrms.hr.doctype.leave_application.leave_application import LeaveApplication
from frappe.utils import getdate, cint
import frappe
from frappe import _
from datetime import timedelta

# Import the logger explicitly for info logging
from frappe.utils.logger import get_logger

# Initialize a logger for your custom app
logger = get_logger(__name__)


class CustomLeaveApplication(LeaveApplication):
    """
    Custom controller for the Leave Application DocType.
    """

    def validate(self):
        super().validate()
        self.calculate_total_leave_days()

    def calculate_total_leave_days(self):
        """
        Custom method to calculate the total number of leave days.
        Holidays are excluded (employee list first, else company list).
        Half-day logic remains unchanged: half of the total period.
        """
        if not self.from_date or not self.to_date:
            frappe.throw(_("From Date and To Date are required to calculate leave days."))

        from_date = getdate(self.from_date)
        to_date = getdate(self.to_date)

        # --- holiday list priority ---
        holiday_list = frappe.get_value("Employee", self.employee, "holiday_list")
        if not holiday_list:
            holiday_list = frappe.get_value("Company", self.company, "default_holiday_list")

        holidays = []
        if holiday_list:
            rows = frappe.get_all(
                "Holiday", filters={"parent": holiday_list}, fields=["holiday_date"]
            )
            holidays = [getdate(h["holiday_date"]) for h in rows]

        # count leave days
        days_in_range = 0
        current_date = from_date

        while current_date <= to_date:
            # Skip holidays completely
            if current_date in holidays:
                current_date += timedelta(days=1)
                continue

            # Saturday (weekday() == 5), if not in the half day then take it as a half day
            if not self.half_day and current_date.weekday() == 5:
                days_in_range += 0.5
            else:
                days_in_range += 0.5 if self.half_day else 1

            current_date += timedelta(days=1)

        self.total_leave_days = days_in_range

    def create_or_update_attendance(self, attendance_name, date):
        status = "Half Day" if self.half_day else "On Leave"

        if attendance_name:
            doc = frappe.get_doc("Attendance", attendance_name)
            doc.db_set({
                "status": status,
                "leave_type": self.leave_type,
                "leave_application": self.name
            })
        else:
            doc = frappe.new_doc("Attendance")
            doc.employee = self.employee
            doc.employee_name = self.employee_name
            doc.attendance_date = date
            doc.company = self.company
            doc.leave_type = self.leave_type
            doc.leave_application = self.name
            doc.status = status
            doc.flags.ignore_validate = True
            doc.insert(ignore_permissions=True)
            doc.submit()
            logger.info(
                f"Created new attendance for {self.employee} on {date} with status {status}.",
                "Custom Leave App Attendance Creation"
            )

    def update_attendance(self):
        """
        Override update_attendance to skip holidays.
        Attendance should only be created if leave status is 'Approved'.
        """
        # Skip if not approved
        if self.status != "Approved":
            return
    
        from_date = getdate(self.from_date)
        to_date = getdate(self.to_date)

        # --- holiday list priority ---
        holiday_list = frappe.get_value("Employee", self.employee, "holiday_list")
        if not holiday_list:
            holiday_list = frappe.get_value("Company", self.company, "default_holiday_list")

        holidays = []
        if holiday_list:
            rows = frappe.get_all(
                "Holiday", filters={"parent": holiday_list}, fields=["holiday_date"]
            )
            holidays = [getdate(h["holiday_date"]) for h in rows]

        current_date = from_date
        while current_date <= to_date:
            try:
                if current_date in holidays:
                    current_date += timedelta(days=1)
                    continue

                # Saturday = Half Day (unless leave application itself is half-day)
                if not self.half_day and current_date.weekday() == 5:
                    status = "Half Day"
                else:
                    status = "Half Day" if self.half_day else "On Leave"

                existing_attendance_name = frappe.db.get_value(
                    "Attendance",
                    {"employee": self.employee, "attendance_date": current_date},
                    "name"
                )

                if existing_attendance_name:
                    doc = frappe.get_doc("Attendance", existing_attendance_name)
                    doc.db_set({
                        "status": status,
                        "leave_type": self.leave_type,
                        "leave_application": self.name
                    })
                else:
                    doc = frappe.new_doc("Attendance")
                    doc.employee = self.employee
                    doc.employee_name = self.employee_name
                    doc.attendance_date = current_date
                    doc.company = self.company
                    doc.leave_type = self.leave_type
                    doc.leave_application = self.name
                    doc.status = status
                    doc.flags.ignore_validate = True
                    doc.insert(ignore_permissions=True)
                    doc.submit()

                current_date += timedelta(days=1)

            except Exception as e:
                frappe.log_error(
                    f"Failed to create/update attendance for {self.employee} on {current_date}: {e}",
                    "Custom Leave App Attendance Error"
                )
                frappe.throw(_(f"Error processing attendance for {current_date}: {e}"))