# Copyright (c) 2026, Guba Technology
# License: MIT

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
			return {"ok": False, "error": _(GENERIC_ERROR)}

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
	"""Raise a validation error that is safe to show to a public bidder.

	Translation happens here, at throw time, rather than when the module is
	imported, so the message follows the language of the request.
	"""
	frappe.throw(_(message), BidPortalError)


class BidPortalError(frappe.ValidationError):
	"""A curated, user-facing error raised by the public bid portal."""


GENERIC_ERROR = "Something went wrong while processing your request. Please review your details and try again."

# Curated messages: every one of these is safe to show to an anonymous bidder
# and tells them what to do next instead of exposing an internal failure.
# They are plain strings on purpose - bid_throw translates them at throw time.
NOT_INVITED = (
	"Your company is not on the invited supplier list for this tender. "
	"Please contact the procurement team."
)
BID_ALREADY_RECORDED = (
	"A bid from your company has already been recorded for this tender and is being evaluated. "
	"Please contact the procurement team if you need to amend it."
)
SUPPLIER_NOT_SAVED = "We could not register your company. Please review the details and try again."
QUOTATION_NOT_SAVED = "We could not save your quotation. Please review the details and try again."
SCORE_NOT_SAVED = "We could not save your specification details. Please review the details and try again."
TENDER_CLOSED = "This tender is closed for bids."


def _guard(message, fn):
	"""Run a write and replace an unexpected failure with a curated message.

	Everything ``fn`` touches is rolled back by the endpoint wrapper, so this
	never leaves a half-written supplier, quotation or score behind.
	"""
	try:
		return fn()
	except BidPortalError:
		raise
	except Exception:
		frappe.logger("bid_portal").exception("Bid Portal write failed")
		bid_throw(message)


def _script_json(data):
	"""Serialise data for an inline script without letting it break out of it."""
	return (
		json.dumps(data, default=str)
		.replace("&", "\\u0026")
		.replace("<", "\\u003c")
		.replace(">", "\\u003e")
	)


def after_request(response=None, request=None):
	"""Keep the bid form (which embeds a CSRF token) out of browser caches.

	Frappe's default headers let a proxy or browser reuse a previously rendered
	form, which then carries an expired token and a stale tender list.
	"""
	if not request or not request.path:
		return
	path = request.path.rstrip("/")
	if path.endswith("/submit_bid"):
		response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
		response.headers["Pragma"] = "no-cache"
		response.headers["Expires"] = "0"


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


def _tender_is_locked(tender_doc):
	return bool(tender_doc and tender_doc.status == "Locked")


def _assert_tender_open(tender_doc):
	"""Reject writes once scoring has started.

	Re-checked immediately before every write so a lock raised part way through
	a request still produces a curated message instead of a generic error.
	"""
	if _tender_is_locked(tender_doc):
		bid_throw(TENDER_CLOSED)


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
	_assert_tender_open(tender_doc)

	return rfq_doc, tender_doc


def _invited_suppliers(rfq_doc):
	"""Suppliers the tender invites.

	An empty table means the tender is open to anyone, so there is nothing to
	enforce and every bidder is allowed through.
	"""
	return [row for row in (rfq_doc.get("suppliers") or []) if row.supplier]


def _resolve_invited_supplier(rfq_doc, supplier_name, tax_id):
	"""Return the supplier this bid belongs to, or refuse the bidder.

	Resolution mirrors :func:`_get_or_create_supplier` (tax id first, then name)
	so the check and the write can never disagree about who is bidding. When the
	tender does invite suppliers, the returned name is authoritative and the
	bid is attached to it even if the entered label differs from the record.
	"""
	invited = _invited_suppliers(rfq_doc)
	if not invited:
		return None

	existing = None
	if tax_id:
		existing = frappe.db.get_value("Supplier", {"tax_id": tax_id}, "name")
	if not existing and supplier_name:
		existing = frappe.db.get_value("Supplier", {"supplier_name": supplier_name}, "name")

	if existing and existing in {row.supplier for row in invited}:
		return existing

	# Not registered yet - the invited link may already carry this company's
	# name, in which case the bid belongs to that supplier rather than a new one.
	if not existing:
		needle = supplier_name.strip().lower()
		if needle:
			for row in invited:
				labels = {row.supplier, row.supplier_name}
				if any((label or "").strip().lower() == needle for label in labels):
					return row.supplier

	bid_throw(NOT_INVITED)


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


def _rfq_currency(company):
	"""Company currency with a system-wide fallback.

	A company without a default currency would otherwise fail validation deep
	inside the quotation save and surface as a generic error.
	"""
	return (
		frappe.db.get_value("Company", company, "default_currency")
		or frappe.get_system_settings("currency")
		or None
	)


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
		"currency": _rfq_currency(rfq_doc.company),
		"items": items,
	}


def _get_or_create_supplier(data, invited=None):
	"""Resolve (and only then, if allowed) register the bidder.

	``invited`` is the supplier the tender invited. It is authoritative: a
	tender that lists its suppliers decides who may bid, so no supplier is ever
	created for an invitation-only tender.
	"""
	settings = get_settings()
	supplier_name = (data.get("supplier_name") or "").strip()
	tax_id = (data.get("tax_id") or "").strip()
	email = (data.get("email") or "").strip()

	existing = invited
	if not existing:
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
			_guard(SUPPLIER_NOT_SAVED, lambda: supplier.save(ignore_permissions=True))
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

	def _create():
		supplier.insert(ignore_permissions=True)
		return supplier.name

	return _guard(SUPPLIER_NOT_SAVED, _create)


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


def _default_warehouse():
	"""Stock Settings default, or ``None`` when it is not configured."""
	try:
		return frappe.db.get_single_value("Stock Settings", "default_warehouse")
	except Exception:
		return None


def _save_supplier_quotation(supplier, rfq_doc, bids, tender_doc):
	_assert_tender_open(tender_doc)

	existing = _find_draft_supplier_quotation(supplier, rfq_doc.name)
	if existing:
		sq = frappe.get_doc("Supplier Quotation", existing)
	else:
		sq = frappe.new_doc("Supplier Quotation")
		sq.supplier = supplier
		sq.company = rfq_doc.company
		sq.currency = _rfq_currency(rfq_doc.company)
		sq.transaction_date = today()

	# Stock items need a warehouse even when the tender did not specify one.
	fallback_warehouse = _default_warehouse()
	schedule_date = rfq_doc.schedule_date or today()

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
		row.warehouse = item.warehouse or fallback_warehouse
		row.schedule_date = item.schedule_date or schedule_date
		row.rate = rate
		row.request_for_quotation = rfq_doc.name
		row.request_for_quotation_item = item.name

	sq.flags.ignore_permissions = True

	def _save():
		sq.save(ignore_permissions=True)
		return sq.name

	return _guard(QUOTATION_NOT_SAVED, _save)


def _save_specification_score(supplier, tender_doc, bids):
	_assert_tender_open(tender_doc)

	# The bidder may only amend a score the portal created. A submitted score -
	# or one the committee owns - is off limits and would otherwise surface as
	# a generic error from validate_duplicate_score.
	existing = frappe.db.get_value(
		"Supplier Specification Score",
		{
			"tender_specification": tender_doc.name,
			"supplier": supplier,
			"docstatus": 0,
			"bid_submission": 1,
		},
		"name",
	)
	if not existing and frappe.db.exists(
		"Supplier Specification Score",
		{
			"tender_specification": tender_doc.name,
			"supplier": supplier,
			"docstatus": ["!=", 2],
		},
	):
		bid_throw(BID_ALREADY_RECORDED)

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

	def _save():
		score.save(ignore_permissions=True)
		return score.name

	return _guard(SCORE_NOT_SAVED, _save)


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

	# Refuse the bidder before anything is written when the tender invites a
	# specific supplier list.
	invited_supplier = _resolve_invited_supplier(
		rfq_doc,
		(payload.get("supplier_name") or "").strip(),
		(payload.get("tax_id") or "").strip(),
	)

	supplier = _get_or_create_supplier(payload, invited_supplier)
	quotation = _save_supplier_quotation(supplier, rfq_doc, bids, tender_doc)
	score = _save_specification_score(supplier, tender_doc, bids)

	frappe.db.commit()

	return {
		"ok": True,
		"supplier": supplier,
		"quotation": quotation,
		"score": score,
		"message": _("Your bid has been received. Reference: {0}").format(quotation),
	}
