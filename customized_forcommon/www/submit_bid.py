# Copyright (c) 2026, Guba Technology
# License: MIT
#
# Public bid submission portal.
#
# Bidders pick an open Request for Quotation, enter their company details, an
# offered specification and a price for every item, and submit. On submit we:
#   * find or create the Supplier,
#   * create/update a draft Supplier Quotation with the prices, and
#   * create/update a draft Supplier Specification Score with the offered specs.
#
# The scoring committee later awards the points on the Specification Score and
# submits it; submitting pushes the technical result into the Quotation
# Comparison Sheet.

import inspect
import json
from functools import wraps

import frappe
import frappe.sessions
from frappe import _
from frappe.utils import flt, today

from customized_forcommon.common_customization.doctype.tender_bidding_settings.tender_bidding_settings import (
	get_settings,
)

# Keep the public portal out of the generated sitemap.
sitemap = 0


def public_endpoint(fn):
	"""Never leak internals from a public endpoint.

	Only messages raised through :class:`BidPortalError` reach the browser.
	Anything else is logged server-side and replaced by a generic message, and
	any partial writes are rolled back.
	"""

	@wraps(fn)
	def wrapper(*args, **kwargs):
		try:
			response = fn(*args, **kwargs)
		except BidPortalError as exc:
			_discard_pending_writes()
			return {"ok": False, "error": frappe.as_unicode(exc)}
		except Exception:
			_discard_pending_writes()
			_log_unexpected_error(fn)
			return {"ok": False, "error": GENERIC_ERROR}

		# Messages queued by frappe.msgprint would otherwise be echoed back to
		# the browser as _server_messages.
		frappe.clear_messages()
		return response

	wrapper.__signature__ = inspect.signature(fn)
	return wrapper


def _discard_pending_writes():
	if frappe.db:
		frappe.db.rollback()
	frappe.clear_messages()


def _log_unexpected_error(fn):
	try:
		frappe.log_error(title=f"Bid Portal: {fn.__name__}", message=frappe.get_traceback())
	except Exception:
		frappe.logger("bid_portal").exception("Bid Portal request failed")
	else:
		# The write above happened after the rollback, so ask the request to keep it.
		frappe.local.flags.commit = True


def bid_throw(message):
	"""Raise a validation error that is safe to show to a public bidder."""
	frappe.throw(message, BidPortalError)


class BidPortalError(frappe.ValidationError):
	"""A curated, user-facing error raised by the public bid portal."""


GENERIC_ERROR = "Something went wrong while processing your request. Please review your details and try again."


def _script_json(data):
	"""Serialise data for an inline script without letting it break out of it."""
	return (
		json.dumps(data, default=str)
		.replace("&", "\\u0026")
		.replace("<", "\\u003c")
		.replace(">", "\\u003e")
	)


def get_context(context):
	context.no_cache = 1
	context.title = _("Submit Bid")
	# Generates and persists the token for the guest session so the POST is valid.
	context.csrf_token = frappe.sessions.get_csrf_token()
	try:
		context.open_rfqs_json = _script_json(_list_open_rfqs())
	except Exception:
		frappe.logger("bid_portal").exception("Could not list open tenders")
		context.open_rfqs_json = "[]"
	return context


def _list_open_rfqs():
	rfqs = frappe.get_all(
		"Request for Quotation",
		filters={"docstatus": 1},
		fields=["name", "subject", "company", "transaction_date"],
		order_by="transaction_date desc",
		limit_page_length=200,
	)

	specs = frappe.get_all(
		"Tender Specification",
		filters={"status": ["!=", "Locked"]},
		fields=["request_for_quotation", "name"],
	)
	spec_by_rfq = {row.request_for_quotation: row.name for row in specs}

	open_rfqs = []
	for rfq in rfqs:
		tender_specification = spec_by_rfq.get(rfq.name)
		if tender_specification:
			rfq["tender_specification"] = tender_specification
			open_rfqs.append(rfq)
	return open_rfqs


def _get_rfq_and_tender(rfq):
	if not rfq:
		bid_throw(_("Please select a tender."))

	if not frappe.db.exists("Request for Quotation", rfq):
		bid_throw(_("The selected tender is no longer open. Please go back and choose again."))

	rfq_doc = frappe.get_doc("Request for Quotation", rfq)
	if rfq_doc.docstatus != 1:
		bid_throw(_("Bids can only be submitted against a submitted tender."))

	tender_name = frappe.db.get_value("Tender Specification", {"request_for_quotation": rfq}, "name")
	if not tender_name:
		bid_throw(_("This tender is not open for bids."))

	tender_doc = frappe.get_doc("Tender Specification", tender_name)
	if tender_doc.status == "Locked":
		bid_throw(_("This tender is closed for bids."))

	return rfq_doc, tender_doc


def _criteria_by_item(tender_doc):
	grouped = {}
	for row in tender_doc.criteria:
		grouped.setdefault(row.item, []).append(
			{
				"component": row.component,
				"recommended_spec": row.recommended_spec,
				"max_points": row.merit_points,
			}
		)
	return grouped


def _rfq_details(rfq):
	rfq_doc, tender_doc = _get_rfq_and_tender(rfq)
	criteria = _criteria_by_item(tender_doc)

	items = []
	for item in rfq_doc.items:
		items.append(
			{
				"item_code": item.item_code,
				"item_name": item.item_name,
				"description": item.description,
				"qty": item.qty,
				"uom": item.uom,
				"criteria": criteria.get(item.item_code, []),
			}
		)

	return {
		"name": rfq_doc.name,
		"subject": rfq_doc.subject,
		"currency": frappe.db.get_value("Company", rfq_doc.company, "default_currency"),
		"items": items,
	}


def _get_or_create_supplier(data):
	settings = get_settings()
	supplier_name = (data.get("supplier_name") or "").strip()
	tax_id = (data.get("tax_id") or "").strip()
	email = (data.get("email") or "").strip()

	existing = None
	if tax_id:
		existing = frappe.db.get_value("Supplier", {"tax_id": tax_id}, "name")
	if not existing:
		existing = frappe.db.get_value("Supplier", {"supplier_name": supplier_name}, "name")

	if existing:
		supplier = frappe.get_doc("Supplier", existing)
		changed = False
		if email and not supplier.email_id:
			supplier.email_id = email
			changed = True
		if tax_id and not supplier.tax_id:
			supplier.tax_id = tax_id
			changed = True
		if changed:
			supplier.save(ignore_permissions=True)
		return supplier.name

	if not flt(settings.auto_create_supplier):
		bid_throw(
			_("Supplier {0} is not registered. Please contact the procurement team.").format(supplier_name)
		)

	supplier = frappe.new_doc("Supplier")
	supplier.supplier_name = supplier_name
	supplier.supplier_type = data.get("supplier_type") or "Company"
	if settings.default_supplier_group:
		supplier.supplier_group = settings.default_supplier_group
	supplier.tax_id = tax_id or None
	supplier.email_id = email or None
	supplier.mobile_no = (data.get("mobile") or "").strip() or None

	country = (data.get("country") or "").strip()
	if country and frappe.db.exists("Country", country):
		supplier.country = country

	supplier.flags.ignore_permissions = True
	supplier.insert(ignore_permissions=True)
	return supplier.name


def _find_draft_supplier_quotation(supplier, rfq):
	names = frappe.get_all(
		"Supplier Quotation", filters={"supplier": supplier, "docstatus": 0}, pluck="name"
	)
	for name in names:
		if frappe.db.exists(
			"Supplier Quotation Item", {"parent": name, "request_for_quotation": rfq}
		):
			return name
	return None


def _save_supplier_quotation(supplier, rfq_doc, bids):
	existing = _find_draft_supplier_quotation(supplier, rfq_doc.name)
	if existing:
		sq = frappe.get_doc("Supplier Quotation", existing)
	else:
		sq = frappe.new_doc("Supplier Quotation")
		sq.supplier = supplier
		sq.company = rfq_doc.company
		sq.currency = frappe.db.get_value("Company", rfq_doc.company, "default_currency")
		sq.transaction_date = today()

	sq.set("items", [])
	for item in rfq_doc.items:
		bid = bids.get(item.item_code) or {}
		rate = flt(bid.get("rate"))
		if rate <= 0:
			continue
		row = sq.append("items", {})
		row.item_code = item.item_code
		row.item_name = item.item_name
		row.description = item.description
		row.qty = item.qty
		row.uom = item.uom
		row.stock_uom = item.stock_uom or item.uom
		row.conversion_factor = 1
		row.warehouse = item.warehouse
		row.schedule_date = item.schedule_date or rfq_doc.schedule_date
		row.rate = rate
		row.request_for_quotation = rfq_doc.name
		row.request_for_quotation_item = item.name

	sq.flags.ignore_permissions = True
	sq.save(ignore_permissions=True)
	return sq.name


def _save_specification_score(supplier, tender_doc, bids):
	existing = frappe.db.get_value(
		"Supplier Specification Score",
		{"tender_specification": tender_doc.name, "supplier": supplier, "docstatus": 0},
		"name",
	)
	if existing:
		score = frappe.get_doc("Supplier Specification Score", existing)
	else:
		score = frappe.new_doc("Supplier Specification Score")
		score.tender_specification = tender_doc.name
		score.supplier = supplier
		score.bid_submission = 1

	score.set("score_details", [])
	for row in tender_doc.criteria:
		bid = bids.get(row.item) or {}
		offered = (bid.get("specs") or {}).get(row.component)
		child = score.append("score_details", {})
		child.item = row.item
		child.component = row.component
		child.recommended_spec = row.recommended_spec
		child.max_points = row.merit_points
		child.supplier_offered_spec = offered

	# Allow the bidder to create their own draft; the committee completes it.
	score.flags.ignore_committee_check = True
	score.flags.ignore_permissions = True
	score.save(ignore_permissions=True)
	return score.name


def _normalise_bids(payload):
	bids = {}
	for row in payload.get("bids") or []:
		item_code = row.get("item_code")
		if not item_code:
			continue
		specs = {}
		for spec in row.get("specs") or []:
			if spec.get("component"):
				specs[spec["component"]] = spec.get("offered")
		bids[item_code] = {"rate": row.get("rate"), "specs": specs}
	return bids


def _validate_bid(payload, bids, rfq_doc):
	"""Reject incomplete bids before anything is written to the database."""

	if not (payload.get("supplier_name") or "").strip():
		bid_throw(_("Company or supplier name is required."))

	if not (payload.get("email") or "").strip():
		bid_throw(_("A contact email is required."))

	offered = 0
	for item in rfq_doc.items:
		if flt((bids.get(item.item_code) or {}).get("rate")) > 0:
			offered += 1

	if not offered:
		bid_throw(_("Please provide a price for at least one item."))


@frappe.whitelist(allow_guest=True)
@public_endpoint
def get_open_rfqs():
	"""Return submitted RFQs that have a Tender Specification."""
	return {"ok": True, "rfqs": _list_open_rfqs()}


@frappe.whitelist(allow_guest=True)
@public_endpoint
def get_rfq_details(rfq=None):
	"""Return the items and their specification criteria for a bidder to fill in."""
	return {"ok": True, "rfq": _rfq_details(rfq)}


@frappe.whitelist(allow_guest=True)
@public_endpoint
def submit_bid(payload=None):
	"""Create the supplier (if needed), a draft quotation and a draft score."""
	if isinstance(payload, str):
		payload = frappe.parse_json(payload)
	payload = payload or {}

	rfq_doc, tender_doc = _get_rfq_and_tender(payload.get("rfq"))
	bids = _normalise_bids(payload)
	_validate_bid(payload, bids, rfq_doc)

	supplier = _get_or_create_supplier(payload)
	quotation = _save_supplier_quotation(supplier, rfq_doc, bids)
	score = _save_specification_score(supplier, tender_doc, bids)

	frappe.db.commit()

	return {
		"ok": True,
		"supplier": supplier,
		"quotation": quotation,
		"score": score,
		"message": _("Your bid has been received. Reference: {0}").format(quotation),
	}
