import calendar
from datetime import datetime

import frappe

class GetLastDay:
    def __init__(self, month_input=None, year=None):
        self.month_input = month_input or datetime.today().month
        self.year = year or datetime.today().year

    def get_last_day(self):
        """Returns the last day of the given month and year."""
        if isinstance(self.month_input, str):
            try:
                month = datetime.strptime(self.month_input, "%B").month  # Full name
            except ValueError:
                try:
                    month = datetime.strptime(self.month_input, "%b").month  # Short name
                except ValueError:
                    month = int(self.month_input)  # Assume numeric string
        else:
            month = int(self.month_input)

        last_day = calendar.monthrange(self.year, month)[1]
        return last_day
    def get_fiscal_year(year,self = None):
            if year == None:
                recent_fy_name = frappe.db.get_value("Fiscal Year",filters={},fieldname="name",order_by="year_start_date desc")
                if recent_fy_name:
                    fy = frappe.get_doc("Fiscal Year", recent_fy_name)
                    year_start = fy.year_start_date
                    year_end = fy.year_end_date
                    return year_start, year_end
            fy = frappe.get_doc("Fiscal Year", year)
            year_start = fy.year_start_date
            year_end = fy.year_end_date
            return year_start, year_end