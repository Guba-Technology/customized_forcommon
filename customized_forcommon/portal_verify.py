# Temporary verification module - removed after use.
import json
import re
import urllib.error
import urllib.request
from http.cookiejar import CookieJar

import frappe
from frappe.utils import today

BASE = "http://127.0.0.1:8000"
HOST = "sugar1.localhost"
MODULE = "customized_forcommon.www.submit_bid"

FAILURES = []
SENSITIVE = [
    "Traceback",
    "exc_type",
    "_server_messages",
    "DocType",
    "/home/kelem",
    'File "',
    "Internal Server Error",
    "sugar1",
    "ValidationError",
    "frappe.exceptions",
    "suppliers",
]


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}{(' :: ' + str(detail)) if detail else ''}")
    if not condition:
        FAILURES.append(f"{label} :: {detail}")


class Client:
    def __init__(self):
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(CookieJar())
        )
        self.token = None

    def get(self, path):
        req = urllib.request.Request(BASE + path, headers={"Host": HOST})
        with self.opener.open(req, timeout=90) as res:
            return res.status, res.read().decode("utf-8", "replace")

    def post(self, method, payload):
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            BASE + "/api/method/" + method,
            data=body,
            method="POST",
            headers={
                "Host": HOST,
                "Content-Type": "application/json",
                "X-Frappe-CSRF-Token": self.token or "",
            },
        )
        try:
            with self.opener.open(req, timeout=90) as res:
                return res.status, res.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace")

    def call(self, method, payload=None):
        status, text = self.post(f"{MODULE}.{method}", payload or {})
        try:
            data = json.loads(text)
        except Exception:
            data = {"__raw": text[:500]}
        return status, data, text


def leaky(text):
    return [token for token in SENSITIVE if token in text]


def refresh():
    """Drop the REPEATABLE-READ snapshot so DB checks see other transactions."""
    frappe.db.rollback()


def setup_tender(with_suppliers=True):
    company = frappe.get_all("Company", pluck="name", limit=1)[0]
    item_code = frappe.get_all("Item", pluck="item_code", limit=1)[0]
    existing_supplier = frappe.get_all("Supplier", pluck="name", limit=1)[0]
    warehouse = (
        frappe.db.get_value("Request for Quotation Item", {"warehouse": ["is", "set"]}, "warehouse")
        or frappe.db.get_value("Warehouse", {"company": company, "is_group": 0}, "name")
    )

    rfq = frappe.new_doc("Request for Quotation")
    rfq.company = company
    rfq.transaction_date = today()
    rfq.schedule_date = today()
    rfq.subject = "Portal verify tender"
    if with_suppliers:
        rfq.append("suppliers", {"supplier": existing_supplier})
    rfq.append(
        "items",
        {
            "item_code": item_code,
            "item_name": "Portal verify item",
            "description": "Portal verify item",
            "qty": 5,
            "uom": frappe.db.get_value("Item", item_code, "stock_uom"),
            "warehouse": warehouse,
            "conversion_factor": 1,
            "rate": 100,
            "schedule_date": today(),
        },
    )
    rfq.insert(ignore_permissions=True)
    rfq.submit()

    spec = frappe.new_doc("Tender Specification")
    spec.request_for_quotation = rfq.name
    spec.append(
        "criteria",
        {
            "item": item_code,
            "component": "Verify Criterion A",
            "recommended_spec": "Grade A",
            "merit_points": 60,
        },
    )
    spec.append(
        "criteria",
        {
            "item": item_code,
            "component": "Verify Criterion B",
            "recommended_spec": "Grade B",
            "merit_points": 40,
        },
    )
    spec.insert(ignore_permissions=True)
    frappe.db.commit()
    return rfq.name, spec.name, item_code, existing_supplier


def _force_delete(doctype, name):
    """Delete a document, cancelling it first if it is submitted."""
    if not name or not frappe.db.exists(doctype, name):
        return
    docstatus = frappe.db.get_value(doctype, name, "docstatus")
    if docstatus == 1:
        frappe.get_doc(doctype, name).cancel()
    frappe.delete_doc(doctype, name, ignore_permissions=True, force=True)


def teardown(rfq, spec, supplier=None, score=None, quotation=None):
    # Remove any score attached to this tender (the portal may have created one
    # for an invited supplier that already existed).
    if spec and frappe.db.exists("Tender Specification", spec):
        for name in frappe.get_all(
            "Supplier Specification Score", {"tender_specification": spec}, pluck="name"
        ):
            _force_delete("Supplier Specification Score", name)

    # Remove any quotation linked to this RFQ.
    if rfq:
        for name in frappe.get_all(
            "Supplier Quotation Item", {"request_for_quotation": rfq}, pluck="parent", distinct=True
        ):
            _force_delete("Supplier Quotation", name)

    for doctype, name in (
        ("Supplier Specification Score", score),
        ("Supplier Quotation", quotation),
        ("Supplier", supplier),
        ("Tender Specification", spec),
        ("Request for Quotation", rfq),
    ):
        _force_delete(doctype, name)
    frappe.db.commit()


def cleanup_leftovers():
    for rfq in frappe.get_all(
        "Request for Quotation", {"subject": "Portal verify tender"}, pluck="name"
    ):
        _delete_rfq_tree(rfq)

    for name in frappe.get_all(
        "Supplier", {"supplier_name": "Portal Verify Supplier"}, pluck="name"
    ):
        _force_delete("Supplier", name)
    frappe.db.commit()
    frappe.db.rollback()


def _delete_rfq_tree(rfq):
    for spec in frappe.get_all(
        "Tender Specification", {"request_for_quotation": rfq}, pluck="name"
    ):
        for name in frappe.get_all(
            "Supplier Specification Score", {"tender_specification": spec}, pluck="name"
        ):
            _force_delete("Supplier Specification Score", name)
        _force_delete("Tender Specification", spec)
    for name in frappe.get_all(
        "Supplier Quotation Item",
        {"request_for_quotation": rfq},
        pluck="parent",
        distinct=True,
    ):
        _force_delete("Supplier Quotation", name)
    _force_delete("Request for Quotation", rfq)


def run():
    cleanup_leftovers()
    rfq, spec, item_code, invited_supplier = setup_tender(with_suppliers=True)
    supplier_name = "Portal Verify Supplier"
    if frappe.db.exists("Supplier", supplier_name):
        frappe.delete_doc("Supplier", supplier_name, ignore_permissions=True, force=True)
        frappe.db.commit()

    client = Client()
    try:
        # ---- page ----
        status, html = client.get("/submit_bid")
        check("page renders 200", status == 200, status)
        check("page is standalone (no navbar/footer)", not leaky_navbar(html))
        check("page has no anchors or href links", ("<a " not in html and "href=" not in html))
        check("page has no base template footer text", "Built on Frappe" not in html)

        token = re.search(r'window\.BID_CSRF = "([^"]+)"', html)
        check("csrf token rendered", bool(token) and len(token.group(1)) > 10, token and token.group(1)[:8])
        client.token = token.group(1) if token else None

        rfqs_json = re.search(r"window\.BID_RFQS = (\[.*?\]);", html, re.S)
        check("open rfqs injected as json", bool(rfqs_json), None)

        # ---- open rfqs ----
        status, data, raw = client.call("get_open_rfqs")
        msg = data.get("message") or {}
        check("get_open_rfqs 200", status == 200, status)
        check("get_open_rfqs ok", msg.get("ok") is True, msg)
        check("get_open_rfqs has no leaks", not leaky(raw), None)

        # ---- details (valid) ----
        status, data, raw = client.call("get_rfq_details", {"rfq": rfq})
        msg = data.get("message") or {}
        details = msg.get("rfq") or {}
        check("get_rfq_details 200", status == 200, status)
        check("get_rfq_details ok", msg.get("ok") is True, msg)
        check(
            "get_rfq_details carries criteria",
            bool(details.get("items")) and bool(details["items"][0].get("criteria")),
            details,
        )

        # ---- details (missing rfq) ----
        status, data, raw = client.call("get_rfq_details", {"rfq": "DOES-NOT-EXIST"})
        msg = data.get("message") or {}
        check("missing rfq returns 200", status == 200, status)
        check("missing rfq is ok:false", msg.get("ok") is False, msg)
        check("missing rfq message is curated", "no longer open" in str(msg.get("error", "")), msg)
        check("missing rfq has no leaks", not leaky(raw), None)

        # ---- unexpected server error ----
        status, data, raw = client.call("submit_bid", {"payload": ["not", "a", "dict"]})
        msg = data.get("message") or {}
        check("unexpected error returns 200", status == 200, status)
        check("unexpected error is ok:false", msg.get("ok") is False, msg)
        check(
            "unexpected error uses generic message",
            "Something went wrong" in str(msg.get("error", "")),
            msg,
        )
        check("unexpected error has no leaks", not leaky(raw), None)
        refresh()
        check(
            "unexpected error logged",
            bool(frappe.db.get_value("Error Log", {"method": "Bid Portal: submit_bid"}, "name")),
            None,
        )

        # ---- validation (no writes) ----
        suppliers_before = frappe.db.count("Supplier")
        status, data, raw = client.call(
            "submit_bid",
            {"payload": json.dumps({"rfq": rfq, "bids": [{"item_code": item_code, "rate": "10"}]})},
        )
        msg = data.get("message") or {}
        check("validation error is ok:false", msg.get("ok") is False, msg)
        check("validation message is curated", "name is required" in str(msg.get("error", "")), msg)
        check("validation has no leaks", not leaky(raw), None)
        refresh()
        check("validation wrote nothing", frappe.db.count("Supplier") == suppliers_before, None)

        # ---- not-invited supplier is refused, nothing written ----
        suppliers_before = frappe.db.count("Supplier")
        payload = {
            "rfq": rfq,
            "supplier_name": supplier_name,
            "email": "verify@example.com",
            "mobile": "0900000000",
            "country": "Ethiopia",
            "bids": [
                {
                    "item_code": item_code,
                    "rate": "123.45",
                    "specs": [
                        {"component": "Verify Criterion A", "offered": "Grade A+"},
                        {"component": "Verify Criterion B", "offered": "Grade B+"},
                    ],
                }
            ],
        }
        status, data, raw = client.call("submit_bid", {"payload": json.dumps(payload)})
        msg = data.get("message") or {}
        check("not-invited submit is ok:false", msg.get("ok") is False, msg)
        check(
            "not-invited message is curated",
            "not on the invited supplier list" in str(msg.get("error", "")),
            msg,
        )
        check("not-invited has no leaks", not leaky(raw), None)
        refresh()
        check("not-invited wrote no supplier", frappe.db.count("Supplier") == suppliers_before, None)
        check(
            "not-invited wrote no quotation",
            not frappe.db.exists("Supplier Quotation", {"supplier": supplier_name}),
            None,
        )

        # ---- invited supplier succeeds ----
        invited_payload = dict(payload)
        invited_payload["supplier_name"] = invited_supplier
        invited_payload["email"] = "invited@example.com"
        status, data, raw = client.call("submit_bid", {"payload": json.dumps(invited_payload)})
        msg = data.get("message") or {}
        check("invited submit 200", status == 200, status)
        check("invited submit ok", msg.get("ok") is True, msg)
        check("invited submit returns a reference", bool(msg.get("quotation")), msg)
        check("invited submit has no leaks", not leaky(raw), None)

        quotation = msg.get("quotation")
        score = msg.get("score")
        refresh()
        check("invited quotation created", bool(quotation and frappe.db.exists("Supplier Quotation", quotation)), None)
        check("invited score created", bool(score and frappe.db.exists("Supplier Specification Score", score)), None)

        # ---- locked tender refuses portal writes ----
        refresh()
        frappe.db.set_value("Tender Specification", spec, "status", "Locked")
        frappe.db.commit()
        refresh()
        check(
            "tender is locked in db",
            frappe.db.get_value("Tender Specification", spec, "status") == "Locked",
            frappe.db.get_value("Tender Specification", spec, "status"),
        )
        status, data, raw = client.call("submit_bid", {"payload": json.dumps(invited_payload)})
        msg = data.get("message") or {}
        check("locked submit is ok:false", msg.get("ok") is False, msg)
        check("locked message is curated", "closed for bids" in str(msg.get("error", "")), msg)
        check("locked has no leaks", not leaky(raw), None)

        # ---- locked tender blocks desk-side Supplier Quotation update ----
        blocked = False
        if quotation:
            try:
                sq = frappe.get_doc("Supplier Quotation", quotation)
                sq.transaction_date = today()
                sq.save(ignore_permissions=True)
            except frappe.ValidationError:
                blocked = True
            except Exception as exc:
                blocked = "locked" in str(exc).lower()
        refresh()
        check("locked tender blocks Supplier Quotation update", blocked, None)

        # ---- locked tender still allows committee score submit ----
        committee_ok = False
        if score:
            try:
                sc = frappe.get_doc("Supplier Specification Score", score)
                for row in sc.score_details:
                    if row.points_awarded in (None, ""):
                        row.points_awarded = row.max_points
                sc.flags.ignore_permissions = True
                sc.submit()
                committee_ok = True
            except Exception as exc:
                committee_ok = f"error: {exc}"
        refresh()
        check("locked tender allows committee score submit", committee_ok is True, committee_ok)

    finally:
        teardown(rfq, spec, supplier_name)

    print("\n=== SUMMARY ===")
    if FAILURES:
        print(f"{len(FAILURES)} FAILURE(S)")
        for f in FAILURES:
            print(" -", f)
    else:
        print("ALL CHECKS PASSED")


def leaky_navbar(html):
    lowered = html.lower()
    for marker in ("navbar", "website-toolbar", "built on frappe", "<footer"):
        if marker in lowered:
            return marker
    return None
