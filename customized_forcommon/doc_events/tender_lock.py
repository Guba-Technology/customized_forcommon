# Copyright (c) 2026, Guba Technology
# License: MIT

"""Freeze tender data once scoring has started.

Locking a Tender Specification means the committee is evaluating what was
submitted, so nothing under it may change any more - not the bidder's
quotation and not the specification details they sent in. These guards live
in ``doc_events`` because the desk, the API and the public portal all reach
the same doctypes, and none of them may bypass the freeze.
"""

import frappe
from frappe import _


def _locked_tender_for_rfq(request_for_quotation):
	"""Return the name of the tender if the RFQ's tender is locked."""
	if not request_for_quotation:
		return None
	name = frappe.db.get_value(
		"Tender Specification", {"request_for_quotation": request_for_quotation}, "name"
	)
	if not name:
		return None
	status = frappe.db.get_value("Tender Specification", name, "status")
	return name if status == "Locked" else None


def _is_tender_committee_member(tender_specification, user=None):
	"""True when the user may still work on a locked tender's scoring."""
	user = user or frappe.session.user
	if user == "Administrator":
		return True
	if not tender_specification:
		return False
	return user in frappe.get_all(
		"Tender Specification Committee Member",
		filters={"parent": tender_specification},
		pluck="user",
	)


def validate_supplier_quotation(doc, method=None):
	"""Refuse any change to a quotation whose tender is locked.

	The links are read straight from the database so a bidder cannot dodge the
	check by clearing the ``request_for_quotation`` field before saving.
	"""
	if doc.is_new():
		return

	rows = doc.get("items") or []
	linked = {row.request_for_quotation for row in rows if row.request_for_quotation}
	existing = frappe.get_all(
		"Supplier Quotation Item",
		filters={"parent": doc.name, "request_for_quotation": ["is", "set"]},
		pluck="request_for_quotation",
	)
	linked.update(existing)

	for request_for_quotation in linked:
		tender = _locked_tender_for_rfq(request_for_quotation)
		if tender:
			frappe.throw(
				_(
					"Tender Specification {0} is locked, so Supplier Quotation {1} can no longer be changed."
				).format(tender, doc.name)
			)


def validate_supplier_specification_score(doc, method=None):
	"""Refuse changes to a submitted specification score once the tender is locked.

	The committee has to keep scoring after the lock - that is what the lock
	signals - so a committee member (or the flag set by their workflow) is
	allowed through. Everyone else, and every portal submission, is frozen.
	"""
	if not doc.tender_specification:
		return

	status = frappe.db.get_value(
		"Tender Specification", doc.tender_specification, "status"
	)
	if status != "Locked":
		return

	if doc.flags.get("ignore_lock_check") or _is_tender_committee_member(doc.tender_specification):
		return

	frappe.throw(
		_(
			"Tender Specification {0} is locked, so its specification scores can no "
			"longer be changed."
		).format(doc.tender_specification)
	)
