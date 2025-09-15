# Copyright (c) 2025, Guba Technology and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from customized_forcommon.custom_report.my_utilities.get_company_info import GetCompanyInfo

class EmployeePensionReport:
    def __init__(self, filters=None):
        self.filters = filters or {}
        self.conditions = {}
        self.columns = self.get_columns()
        self.get_company_info = GetCompanyInfo()

    def run(self):
        if not self.has_required_accounts():
            self.throw_missing_account_error()

        self.build_conditions()
        data = self.get_data()
        return self.columns, data

    def has_required_accounts(self):
        return self.get_company_info.get_pension_payable_account() or self.get_company_info.get_pension_receivable_account()

    def throw_missing_account_error(self):
        frappe.throw(
            _("Pension payable account or pension receivable account not found. Please set in <a href='/app/company/{0}'>{0}</a> <br> available at <b>VAT Account</b> tab").format(
                self.get_company_info.Company
            )
        )

    def build_conditions(self):
        filter_fields = ["name", "tin_number", "employee_name",  "ctc"]
        self.filters["docstatus"] = 1
        for field in filter_fields:
            if self.filters.get(field):
                self.conditions[field] = ["like", f"%{self.filters.get(field)}%"]

        for date_field in ["date_of_joining", "relieving_date"]:
            condition = self.get_date_condition(date_field, self.filters.get(date_field), self.filters.get("is_range"))
            if condition:
                self.conditions[date_field] = condition

    def get_date_condition(self, field_name, date_value, is_range):
        if not date_value:
            return None
        return (">=", date_value) if is_range else ("=", date_value)

    def get_columns(self):
        return [
            {"label": "Employee", "fieldname": "name", "fieldtype": "Link", "options": "Employee", "width": 200},
            {"label": "Employee TIN", "fieldname": "tin_number", "fieldtype": "Data"},
            {"label": "Full Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
            
            {"label": "Start Date", "fieldname": "date_of_joining", "fieldtype": "Date"},
            {"label": "End Date", "fieldname": "relieving_date", "fieldtype": "Date"},
            {"label": "Basic Salary", "fieldname": "ctc", "fieldtype": "Float"},
        ]

    def get_data(self):
        employees = frappe.get_all(
            "Employee",
            fields=[
                "name", "tin_number", "employee_name", "middle_name", "last_name",
                "date_of_joining", "relieving_date", "ctc"
            ],
            filters=self.conditions,
        )

        return [
            {
                "name": emp.name,
                "tin_number": emp.tin_number,
                "employee_name": emp.employee_name,
               
                "date_of_joining": emp.date_of_joining,
                "relieving_date": emp.relieving_date,
                "ctc": emp.ctc,
            }
            for emp in employees
        ]
def execute(filters=None):
    return EmployeePensionReport(filters).run()
