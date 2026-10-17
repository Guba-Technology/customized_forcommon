# Copyright (c) 2026, Guba Technology
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

TOTAL_POINTS_PER_ITEM = 100


class TenderSpecification(Document):
	def validate(self):
		self.validate_locked()
		self.validate_unique_per_rfq()
		self.validate_criteria_per_item()
		self.set_status()

	def validate_locked(self):
		"""Once scoring has started the specification rows/points are frozen."""
		if self.is_new():
			return
		previous_status = frappe.db.get_value("Tender Specification", self.name, "status")
		if previous_status != "Locked":
			return

		previous = self.get_doc_before_save()
		if not previous:
			return

		def signature(rows):
			return [(r.item, r.component, r.recommended_spec, r.merit_points) for r in rows or []]

		if signature(previous.criteria) != signature(self.criteria):
			frappe.throw(
				_("Tender Specification {0} is Locked and can no longer be edited.").format(self.name)
			)

	def validate_unique_per_rfq(self):
		"""Only one tender specification is allowed per Request for Quotation."""
		if not self.request_for_quotation:
			return
		existing = frappe.db.exists(
			"Tender Specification",
			{
				"request_for_quotation": self.request_for_quotation,
				"name": ["!=", self.name or ""],
			},
		)
		if existing:
			frappe.throw(
				_("A Tender Specification already exists for Request for Quotation {0}: {1}").format(
					self.request_for_quotation, existing
				)
			)

	def validate_criteria_per_item(self):
		"""Every item's criteria merit points must add up to exactly 100."""
		totals = {}
		for row in self.criteria:
			if not row.item:
				frappe.throw(_("Row #{0}: Item is required.").format(row.idx))
			totals[row.item] = totals.get(row.item, 0) + flt(row.merit_points)

		if not totals:
			frappe.throw(_("Please add at least one criteria row."))

		for item, total in totals.items():
			if flt(total, 2) != TOTAL_POINTS_PER_ITEM:
				frappe.throw(
					_("Item {0}: total merit points must be exactly 100 (currently {1}).").format(
						item, flt(total, 2)
					)
				)

	def before_insert(self):
		self.validate_committee_members()

	def validate_committee_members(self):
		for row in self.committee_members or []:
			if not row.user:
				frappe.throw(_("Row #{0}: Committee Member is required.").format(row.idx))

	def set_status(self):
		"""Draft becomes Open for Scoring as soon as committee members are added."""
		if self.status == "Draft" and self.committee_members:
			self.status = "Open for Scoring"

	def get_item_criteria(self):
		"""Return this tender's criteria grouped by item, in row order."""
		grouped = {}
		for row in self.criteria:
			grouped.setdefault(row.item, []).append(row)
		return grouped


@frappe.whitelist()
def get_template_items(request_for_quotation):
	"""Build criteria rows for every RFQ item from its standard Item Specification Template.

	Items without a standard template are added as a single blank row so the
	preparer can fill them in manually.
	"""
	if not request_for_quotation:
		frappe.throw(_("Please select a Request for Quotation first."))

	rfq = frappe.get_doc("Request for Quotation", request_for_quotation)
	rows = []

	for item in rfq.items:
		if not item.item_code:
			continue

		template = frappe.db.get_value(
			"Item Specification Template",
			{"item": item.item_code, "is_standard": 1},
			"name",
		)

		template_rows = []
		if template:
			template_rows = frappe.get_all(
				"Item Specification Template Criteria",
				filters={"parent": template},
				fields=["component", "recommended_spec", "merit_points"],
				order_by="idx",
			)

		if template_rows:
			for template_row in template_rows:
				rows.append(
					{
						"item": item.item_code,
						"component": template_row.component,
						"recommended_spec": template_row.recommended_spec,
						"merit_points": template_row.merit_points,
					}
				)
		else:
			rows.append(
				{
					"item": item.item_code,
					"component": "",
					"recommended_spec": "",
					"merit_points": 0,
				}
			)

	return rows


def get_tender_specification_for_rfq(request_for_quotation):
	"""Return the Tender Specification name for an RFQ, if any."""
	if not request_for_quotation:
		return None
	return frappe.db.get_value(
		"Tender Specification",
		{"request_for_quotation": request_for_quotation},
		"name",
	)


def lock_tender_specification(tender_specification):
	"""Called when the first Supplier Specification Score is submitted."""
	if not tender_specification:
		return
	frappe.db.set_value("Tender Specification", tender_specification, "status", "Locked")
