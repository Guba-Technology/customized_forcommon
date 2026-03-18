import frappe
from hrms.hr.doctype.attendance.attendance import Attendance
from frappe import _

class CustomAttendance(Attendance):

    def on_submit(self):
        # super().on_submit()
        if self.status in ["Present", "Half Day","Work From Home"]:
            self.insert_into_attendance_collection()

    def insert_into_attendance_collection(self):
        is_holiday = self.is_date_holiday()

        checkins = frappe.get_all(
            "Employee Checkin",
            filters={"attendance": self.name},
            fields=["name", "time", "log_type", "offshift", "shift"],
            order_by="time asc"
        )

        has_offshift = any(c.offshift for c in checkins)

        if not (is_holiday or has_offshift):
            return

        pairs = self.get_in_out_pairs(checkins)
     
        self.update_collection_record(pairs, is_holiday)

    def is_date_holiday(self):
        holiday_list = None
        if self.shift:
            holiday_list = frappe.db.get_value("Shift Type", self.shift, "holiday_list")
            
        if not holiday_list and self.company:
            holiday_list = frappe.db.get_value("Company", self.company, "default_holiday_list")

        if holiday_list:
            return frappe.db.exists("Holiday", {
                "parent": holiday_list,
                "holiday_date": self.attendance_date
            })
        return False

    def get_in_out_pairs(self, checkins):
        if not checkins:
            return [{"inn": None, "out": None, "checkin_ref": None}]

        pairs = []
        current_in = None

        for log in checkins:
            if log.log_type == "IN":
                if current_in:
                    pairs.append({"inn": current_in.time, "out": None, "checkin_ref": current_in.name})
                current_in = log
            elif log.log_type == "OUT":
                if current_in:
                    pairs.append({"inn": current_in.time, "out": log.time, "checkin_ref": current_in.name})
                    current_in = None
                else:
                    pairs.append({"inn": None, "out": log.time, "checkin_ref": log.name})

        if current_in:
            pairs.append({"inn": current_in.time, "out": None, "checkin_ref": current_in.name})

        return pairs

    def update_collection_record(self, pairs, is_holiday):
        collection_name = frappe.db.get_value("Attendance Collection", {"employee": self.employee}, "name")

        if collection_name:
            doc = frappe.get_doc("Attendance Collection", collection_name)
        else:
            doc = frappe.new_doc("Attendance Collection")
            doc.employee = self.employee
            doc.employee_name = self.employee_name

        # 1. Clear existing rows for THIS attendance record only to prevent duplicates within the child table
        existing_rows = doc.get("employee_checkin_list", [])
        doc.set("employee_checkin_list", [row for row in existing_rows if row.attendance != self.name])

        for pair in pairs:
            checkin_ref = pair.get("checkin_ref")
            
            # 2. Check if this specific checkin/pair is already in the Log
            # We check by employee and employee_checkin (the unique ID of the log)
            log_exists = frappe.db.exists("Attendance Collection Log", {
                "employee": self.employee,
                "employee_checkin": checkin_ref,
                "status": "Paid" # Only skip if it was actually processed/paid
            })

            if log_exists:
                # Skip this pair because it has already been utilized/paid
                continue

            # 3. If not in log, add it to the collection for processing
            doc.append("employee_checkin_list", {
                "attendance_date": self.attendance_date,
                "inn": pair.get("inn"),
                "out": pair.get("out"),
                "employee_checkin": checkin_ref, 
                "attendance": self.name,
                "shift_type": self.shift if self.shift else None,
                "status": "New"
            })

        # 4. Only save if the document was modified (prevents unnecessary database hits)
        if doc.get("employee_checkin_list") or collection_name:
            doc.save(ignore_permissions=True)