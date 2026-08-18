
NET_HOURS_FIELD = "hour_rate"                      
COST_COMPONENTS_FIELD = "custom_cost_components"    

import frappe
from frappe import _
from frappe.utils import flt

from erpnext.accounts.general_ledger import make_gl_entries, make_reverse_gl_entries


def make_workstation_cost_gl_entries(doc, method=None):
	print("Making workstation cost GL entries for Job Card", doc.name)
	if not doc.get("workstation"):
		print("No workstation selected for Job Card", doc.name)
		return

	workstation = frappe.get_cached_doc("Workstation", doc.workstation)
	cost_component_rows = workstation.get(COST_COMPONENTS_FIELD) or []
	if not cost_component_rows:
		print("No cost components found for Workstation", workstation.name)
		return

	net_hours = flt(workstation.get(NET_HOURS_FIELD))
	if not net_hours:
		print("No net hours found for Workstation", workstation.name)
		return

	company = doc.company
	posting_date = doc.posting_date
	job_card_hours = flt(doc.get("total_time_in_mins"))/60 or 0.0
	if not job_card_hours:
		print("No total time in minutes found for Job Card", doc.name)
		return
	gl_map = []
	total_amount = 0.0

	for row in cost_component_rows:
		if not row.cost_component or not row.operating_cost:
			print("Missing cost component or operating cost for Workstation Operating Component", row.name)
			continue

		amount = flt(row.operating_cost) * job_card_hours
		if not amount:
			print("No operating cost found for Workstation Operating Component", row.name)
			continue

		account, cost_center = _get_component_expense_account(row.cost_component, company)
		total_amount += amount

		gl_map.append(
			frappe._dict(
				{
					"account": account,
					"cost_center": cost_center,
					"debit": amount,
					"credit": 0,
					"debit_in_account_currency": amount,
					"credit_in_account_currency": 0,
					"voucher_type": doc.doctype,
					"voucher_no": doc.name,
					"voucher_detail_no": row.name,
					"company": company,
					"posting_date": posting_date,
					"against": None,
					"remarks": _("Workstation operating cost ({0}) for Job Card {1}").format(
						row.cost_component, doc.name
					),
				}
			)
		)

	if not gl_map:
		print("No GL entries to make for Job Card", doc.name)
		return

	expenses_included_in_valuation = frappe.get_cached_value(
		"Company", company, "expenses_included_in_valuation"
	)

	for entry in gl_map:
		entry.against = expenses_included_in_valuation


	credit_cost_center = doc.get("cost_center") or gl_map[0].cost_center

	gl_map.append(
		frappe._dict(
			{
				"account": expenses_included_in_valuation,
				"cost_center": credit_cost_center,
				"debit": 0,
				"credit": total_amount,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": total_amount,
				"against": ", ".join(sorted({d.account for d in gl_map if d.account})),
				"voucher_type": doc.doctype,
				"voucher_no": doc.name,
				"company": company,
				"posting_date": posting_date,
				"remarks": _("Workstation operating cost against Job Card {0}").format(doc.name),
			}
		)
	)

	make_gl_entries(gl_map, cancel=False, update_outstanding="No")


def cancel_workstation_cost_gl_entries(doc, method=None):
	make_reverse_gl_entries(voucher_type=doc.doctype, voucher_no=doc.name)


def _get_component_expense_account(cost_component, company):

	print("Fetching component expense account for Cost Component", cost_component)
	component = frappe.get_cached_doc("Workstation Operating Component", cost_component)
	for row in component.get("component_expense_account") or []:
		if row.company == company:
			return row.expense_account, row.cost_center
	print("No component expense account found for Cost Component", cost_component)
	return None, None