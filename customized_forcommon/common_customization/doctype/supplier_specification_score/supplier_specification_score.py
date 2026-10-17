# Copyright (c) 2026, Guba Technology
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from customized_forcommon.common_customization.doctype.tender_bidding_settings.tender_bidding_settings import (
	get_settings,
)
from customized_forcommon.common_customization.doctype.tender_specification.tender_specification import (
	get_tender_specification_for_rfq,
	lock_tender_specification,
)


class SupplierSpecificationScore(Document):
	def validate(self):
		self.validate_committee_membership()
		self.validate_duplicate_score()
		self.populate_score_details()
		self.validate_points_awarded()
		self.calculate()

	def before_submit(self):
		self.validate_all_points_present()
		self.calculate()

	def on_submit(self):
		# Scoring has started -> freeze the specification rows/points.
		lock_tender_specification(self.tender_specification)
		# Push the specification result into the Quotation Comparison Sheet.
		push_specification_scores_to_comparison_sheet(self.tender_specification)

	def validate_committee_membership(self):
		"""Only members of the tender's committee may create/submit a score.

		Bids coming from the online portal set ``ignore_committee_check`` on the
		document so that the bidder can create their own draft. The committee
		still completes the awarded points and submits it.
		"""
		if self.flags.get("ignore_committee_check"):
			return
		if frappe.session.user == "Administrator":
			return
		if not self.tender_specification:
			return
		members = frappe.get_all(
			"Tender Specification Committee Member",
			filters={"parent": self.tender_specification},
			pluck="user",
		)
		if frappe.session.user not in members:
			frappe.throw(
				_("You are not a committee member of Tender Specification {0} and cannot score it.").format(
					self.tender_specification
				)
			)

	def validate_duplicate_score(self):
		existing = frappe.db.exists(
			"Supplier Specification Score",
			{
				"tender_specification": self.tender_specification,
				"supplier": self.supplier,
				"name": ["!=", self.name or ""],
				"docstatus": ["!=", 2],
			},
		)
		if existing:
			frappe.throw(
				_("A specification score already exists for Supplier {0} on Tender Specification {1}: {2}").format(
					self.supplier, self.tender_specification, existing
				)
			)

	def populate_score_details(self):
		"""Build the score rows from the tender specification the first time."""
		if self.score_details or not self.tender_specification:
			return
		for row in frappe.get_all(
			"Tender Specification Criteria",
			filters={"parent": self.tender_specification},
			fields=["item", "component", "recommended_spec", "merit_points"],
			order_by="idx",
		):
			self.append(
				"score_details",
				{
					"item": row.item,
					"component": row.component,
					"recommended_spec": row.recommended_spec,
					"max_points": row.merit_points,
				},
			)

	def validate_points_awarded(self):
		for row in self.score_details:
			if row.points_awarded in (None, ""):
				continue
			if row.points_awarded < 0 or row.points_awarded > (row.max_points or 0):
				frappe.throw(
					_("Row #{0}: Points Awarded must be between 0 and {1}.").format(
						row.idx, row.max_points or 0
					)
				)

	def validate_all_points_present(self):
		for row in self.score_details:
			if row.points_awarded in (None, ""):
				frappe.throw(_("Row #{0}: Points Awarded is required before submitting.").format(row.idx))

	def calculate(self):
		self.total_possible = sum((row.max_points or 0) for row in self.score_details)
		self.total_awarded = sum((row.points_awarded or 0) for row in self.score_details)
		self.score_percent = (
			flt(self.total_awarded / self.total_possible * 100, 2) if self.total_possible else 0
		)
		self.build_item_scores()

	def build_item_scores(self):
		"""Aggregate the flat criteria grid into per-item totals."""
		grouped = {}
		order = []
		for row in self.score_details:
			if not row.item:
				continue
			if row.item not in grouped:
				grouped[row.item] = {"total_awarded": 0.0, "total_possible": 0.0}
				order.append(row.item)
			grouped[row.item]["total_awarded"] += flt(row.points_awarded or 0)
			grouped[row.item]["total_possible"] += flt(row.max_points or 0)

		minimum_score = flt(get_settings().minimum_spec_score)
		self.item_scores = []
		for item in order:
			data = grouped[item]
			percent = (
				flt(data["total_awarded"] / data["total_possible"] * 100, 2)
				if data["total_possible"]
				else 0
			)
			self.append(
				"item_scores",
				{
					"item": item,
					"total_awarded": data["total_awarded"],
					"total_possible": data["total_possible"],
					"score_percent": percent,
					"is_qualified": 1 if percent >= minimum_score else 0,
				},
			)


@frappe.whitelist()
def get_spec_criteria(tender_specification):
	"""Return the criteria rows of a Tender Specification for the score form."""
	if not tender_specification:
		return []
	return frappe.get_all(
		"Tender Specification Criteria",
		filters={"parent": tender_specification},
		fields=["item", "component", "recommended_spec", "merit_points"],
		order_by="idx",
	)


def get_rfq_specification_scores(request_for_quotation):
	"""Return submitted specification scores for an RFQ.

	Shape::

		{
			"<supplier>": {
				"score_percent": 82.5,
				"total_awarded": 82.5,
				"total_possible": 100,
				"items": {"<item_code>": {"score_percent": 80, "is_qualified": 1}},
			}
		}
	"""
	empty = {}
	tender_specification = get_tender_specification_for_rfq(request_for_quotation)
	if not tender_specification:
		return empty

	scores = frappe.get_all(
		"Supplier Specification Score",
		filters={"tender_specification": tender_specification, "docstatus": 1},
		fields=["name", "supplier", "score_percent", "total_awarded", "total_possible"],
	)

	result = {}
	for score in scores:
		items = {}
		for row in frappe.get_all(
			"Supplier Specification Score Item",
			filters={"parent": score.name},
			fields=["item", "score_percent", "is_qualified"],
		):
			items[row.item] = {
				"score_percent": row.score_percent or 0,
				"is_qualified": row.is_qualified or 0,
			}
		result[score.supplier] = {
			"score_percent": score.score_percent or 0,
			"total_awarded": score.total_awarded or 0,
			"total_possible": score.total_possible or 0,
			"items": items,
		}
	return result


def push_specification_scores_to_comparison_sheet(tender_specification):
	"""Push specification results into the draft Quotation Comparison Sheet of the RFQ."""
	if not tender_specification or not frappe.db.exists("DocType", "Quotation Comparison Sheet"):
		return

	request_for_quotation = frappe.db.get_value(
		"Tender Specification", tender_specification, "request_for_quotation"
	)
	if not request_for_quotation:
		return

	comparison_sheet = frappe.db.get_value(
		"Quotation Comparison Sheet",
		{"request_for_quotation": request_for_quotation, "docstatus": 0},
		"name",
	)
	if not comparison_sheet:
		return

	sheet = frappe.get_doc("Quotation Comparison Sheet", comparison_sheet)
	if hasattr(sheet, "fetch_specification_scores"):
		sheet.fetch_specification_scores()


@frappe.whitelist()
def push_specification_score(name):
	"""Manually push a specific score into the Quotation Comparison Sheet."""
	doc = frappe.get_doc("Supplier Specification Score", name)
	frappe.has_permission("Supplier Specification Score", "write", doc, throw=True)
	push_specification_scores_to_comparison_sheet(doc.tender_specification)
	frappe.msgprint(_("Specification result pushed to the Quotation Comparison Sheet."), alert=True)
