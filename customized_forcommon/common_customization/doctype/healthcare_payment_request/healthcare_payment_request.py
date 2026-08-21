# Copyright (c) 2026, Guba Technology and contributors
# For license information, please see license.txt

# import frappe
# Copyright (c) 2026, Common Customization
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, flt, getdate, nowdate
from frappe.utils import getdate, nowdate, get_last_day, get_first_day, date_diff, add_months, flt

MAX_SCHEDULE_ROWS = 240 
EXPENSE_CLAIM_STATUS_MAP = {
	"Paid": "Settled",
	"Unpaid": "Approved",
	"Submitted": "Approved",
	"Rejected": "Approved",
	"Cancelled": "Approved",
}


class HealthcarePaymentRequest(Document):
	def validate(self):
		self.validate_beneficiary()
		self.calculate_contributions()
		if self.payment_by == "Company":
			self.build_deduction_schedule()
		self.calculate_recovery_totals()
		self.validate_dates()



	def validate_dates(self):
		if self.service_date and self.service_date > nowdate():
			frappe.throw(_("Service Date cannot be in the future"))
		if self.schedule_start_date and self.schedule_start_date < self.service_date:
			frappe.throw(_("Schedule Start Date cannot be before Service Date"))
	def validate_beneficiary(self):
		if self.beneficiary_type == "Family" and not self.beneficiary_name:
			frappe.throw(_("Beneficiary Name is required when Beneficiary Type is Family"))

	def check_duplicate(self):
		existing = frappe.db.exists(
			"Healthcare Payment Request",
			{
				"employee": self.employee,
				"service_date": self.service_date,
				"healthcare_provider": self.healthcare_provider,
				"service_amount": self.service_amount,
				"docstatus": ["!=", 2],
				"name": ["!=", self.name or ""],
			},
		)
		if existing:
			frappe.throw(
				_("Healthcare Payment Request {0} already exists for this service").format(
					frappe.get_desk_link("Healthcare Payment Request", existing)
				)
			)

	# ---------- contribution / schedule calculation ----------

	def calculate_contributions(self):
		if not self.service_amount:
			return
		self.company_contribution_amount = flt(
			self.service_amount * flt(self.company_contribution_) / 100, 2
		)
		self.employee_contribution_amount = flt(
			self.service_amount - self.company_contribution_amount, 2
		)

	def build_deduction_schedule(self):
		"""Recompute the planned deduction schedule. Only allowed pre-submit,
		so approved schedules can't be silently rewritten."""
		if self.docstatus != 0:
			return
		if not self.employee_contribution_amount:
			self.set("deduction_schedule", [])
			return
		if not self.deduction_calculation_type:
			return

		monthly = self.get_monthly_deduction_amount()
		self.monthly_deduction_amount = monthly

		self.set("deduction_schedule", [])
		
		# Fallback to today if schedule_start_date is not set
		start_date = getdate(self.schedule_start_date) if getattr(self, "schedule_start_date", None) else getdate(nowdate())
		
		remaining = flt(self.employee_contribution_amount)
		i = 0
		
		while remaining > 0 and i < MAX_SCHEDULE_ROWS:
			due_date = add_months(start_date, i)

			this_amount = monthly if monthly < remaining else remaining
			
			if this_amount > 0:
				self.append(
					"deduction_schedule",
					{
						"due_date": due_date,
						"amount": this_amount,
						"status": "Pending",
					},
				)
				
				remaining = flt(remaining - this_amount, 2)
			
			i += 1
	def get_monthly_deduction_amount(self):
		if self.deduction_calculation_type == "Fixed Amount":
			if not self.fixed_amount:
				frappe.throw(_("Set a Fixed Amount for the deduction"))
			return flt(self.fixed_amount)

		if self.deduction_calculation_type == "No. of Months":
			if not self.no_of_months:
				frappe.throw(_("Set No. of Months for the deduction"))
			return flt(flt(self.employee_contribution_amount) / self.no_of_months, 2)

		if self.deduction_calculation_type == "CTC Rate":
			ctc = frappe.db.get_value("Employee", self.employee, "ctc") or 0
			if not ctc:
				frappe.throw(_("CTC is not set for Employee {0}").format(self.employee))
			if not self.ctc_rate:
				frappe.throw(_("Set the CTC Rate for the deduction"))
			
			return flt(flt(ctc) * flt(self.ctc_rate) / 100, 2)

		frappe.throw(_("Select a Deduction Calculation Type"))


	def calculate_recovery_totals(self):
		if self.payment_by != "Company":
			recovered = 0.0
			outstanding = 0.0
		else:
			recovered = flt(
				sum(flt(d.amount) for d in self.deduction_schedule if d.status == "Recovered")
			)
			
			if self.employee_contribution_amount:
				outstanding = flt(self.employee_contribution_amount - recovered, 2)
			else:
				outstanding = 0.0

		self.total_recovered_amount = recovered
		self.outstanding_amount = outstanding

		if self.docstatus == 1:
			self.db_set(
				{
					"total_recovered_amount": recovered,
					"outstanding_amount": outstanding,
				}
			)
			

	def refresh_status_from_schedule(self):
		
		if self.status not in ("Approved", "Partially Settled", "Settled"):
			return
		if self.outstanding_amount and self.outstanding_amount > 0 and self.total_recovered_amount > 0:
			self.status = "Partially Settled"
		elif self.employee_contribution_amount and flt(self.outstanding_amount) <= 0:
			self.status = "Settled"
		else:
			self.status = "Approved"

	# ---------- submit / cancel ----------

	def before_submit(self):
		self.check_duplicate()
		if self.payment_by == "Company" and not self.deduction_schedule:
			frappe.throw(_("Deduction Schedule could not be built. Check contribution and deduction settings."))
		if self.payment_by == "Company" and not self.salary_component:
			frappe.throw(_("Select a Salary Component to use for the payroll deduction"))

	def on_submit(self):
		self.status = "Approved"
		if self.payment_by == "Company":
			create_due_additional_salaries(self.name)
		elif self.payment_by == "Employee":
			self.create_expense_claim()
		self.db_set("status", self.status)

	def on_cancel(self):
		if self.additional_salary or self.expense_claim:
			frappe.msgprint(
				_("Note: linked Additional Salary / Expense Claim documents are not auto-cancelled. Cancel them separately if required."),
				alert=True,
			)
		self.status = "Draft"

	# ---------- Scenario 2: Employee Pays ----------

	def create_expense_claim(self):
		if self.expense_claim:
			return

		expense_claim = frappe.new_doc("Expense Claim")
		expense_claim.employee = self.employee
		expense_claim.company = self.company
		expense_claim.append(
			"expenses",
			{
				"expense_type": self.expense_claim_type,
				"amount": self.company_contribution_amount,
				"sanctioned_amount": self.company_contribution_amount,
				"description": _("Healthcare reimbursement for {0} ({1})").format(
					self.healthcare_provider, self.name
				),
			},
		)
		expense_claim.insert(ignore_permissions=True)

		self.db_set("expense_claim", expense_claim.name)


# ---------- Scenario 1: Company Pays — scheduled processing ----------

def create_due_additional_salaries(healthcare_payment_request=None):
    filters = {"docstatus": 1, "payment_by": "Company", "status": ["!=", "Settled"]}
    if healthcare_payment_request:
        filters["name"] = healthcare_payment_request

    for req_name in frappe.get_all("Healthcare Payment Request", filters=filters, pluck="name"):
        doc = frappe.get_doc("Healthcare Payment Request", req_name)
        changed = False

        for row in doc.deduction_schedule:
            if row.status != "Pending" or getdate(row.due_date) > getdate(nowdate()):
                continue

            if row.additional_salary:
                continue

            additional_salary = frappe.new_doc("Additional Salary")
            additional_salary.employee = doc.employee
            additional_salary.company = doc.company
            additional_salary.salary_component = doc.salary_component
            additional_salary.type = "Deduction"
            additional_salary.amount = row.amount
            additional_salary.payroll_date = row.due_date
            additional_salary.overwrite_salary_structure_amount = 0
            additional_salary.insert(ignore_permissions=True)
            additional_salary.submit()

            # Update memory state
            row.additional_salary = additional_salary.name
            row.status = "Processed"

            # Directly update child table row in the database
            frappe.db.set_value(
                row.doctype,
                row.name,
                {
                    "additional_salary": additional_salary.name,
                    "status": "Processed",
                },
            )
            
            changed = True
            
            

        if changed:
            doc.db_set("additional_salary", doc.deduction_schedule[-1].additional_salary)
            doc.calculate_recovery_totals()
            doc.refresh_status_from_schedule()
            doc.db_update()


# ---------- Linked-doctype status tracking (hooks.py doc_events) ----------

def update_deduction_on_salary_slip_submit(doc, method=None):
	for row in doc.get("deductions", []):
		if not row.get("additional_salary"):
			continue

		matches = frappe.get_all(
			"Healthcare Payment Deduction",
			filters={"additional_salary": row.additional_salary, "status": "Processed"},
			fields=["name", "parent"],
		)
		for match in matches:
			frappe.db.set_value("Healthcare Payment Deduction", match.name, "status", "Recovered")

			hpr = frappe.get_doc("Healthcare Payment Request", match.parent)
			hpr.calculate_recovery_totals()
			hpr.refresh_status_from_schedule()
			hpr.db_update()


def update_deduction_on_salary_slip_cancel(doc, method=None):

	for row in doc.get("deductions", []):
		if not row.get("additional_salary"):
			continue

		matches = frappe.get_all(
			"Healthcare Payment Deduction",
			filters={"additional_salary": row.additional_salary, "status": "Recovered"},
			fields=["name", "parent"],
		)
		for match in matches:
			frappe.db.set_value("Healthcare Payment Deduction", match.name, "status", "Processed")

			hpr = frappe.get_doc("Healthcare Payment Request", match.parent)
			hpr.calculate_recovery_totals()
			hpr.refresh_status_from_schedule()
			hpr.db_update()


def update_deduction_on_additional_salary_cancel(doc, method=None):
	"""hooks.py doc_event: Additional Salary.on_cancel
	If an Additional Salary generated by a Healthcare Payment Request is
	cancelled before payroll recovers it, reset the corresponding deduction
	row back to Pending (clearing the link) so the scheduler picks it up
	again on its next run."""
	if doc.type != "Deduction":
		return

	matches = frappe.get_all(
		"Healthcare Payment Deduction",
		filters={"additional_salary": doc.name, "status": ["in", ["Processed", "Recovered"]]},
		fields=["name", "parent"],
	)
	for match in matches:
		frappe.db.set_value(
			"Healthcare Payment Deduction",
			match.name,
			{"status": "Pending", "additional_salary": None},
		)

		hpr = frappe.get_doc("Healthcare Payment Request", match.parent)
		hpr.calculate_recovery_totals()
		hpr.refresh_status_from_schedule()
		hpr.db_update()


def update_hpr_from_expense_claim(doc, method=None):
	hpr_name = frappe.db.get_value(
		"Healthcare Payment Request", {"expense_claim": doc.name, "docstatus": 1}, "name"
	)
	if not hpr_name:
		print(f"Healthcare Payment Request not found for Expense Claim {doc.name}")
		return

	new_status = EXPENSE_CLAIM_STATUS_MAP.get(doc.status)
	if doc.has_value_changed("status") and doc.status == "Paid":
		print(f"Updating Healthcare Payment Request {hpr_name} status to {new_status} based on Expense Claim {doc.name} status {doc.status}")
		frappe.db.set_value("Healthcare Payment Request", hpr_name, "status", "Settled")
