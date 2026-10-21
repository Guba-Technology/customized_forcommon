import frappe


PROCUREMENT_TYPES = [
    {
        "procurement_type": "Goods",
        "sub_type": "",
        "tender_line_basis": "Item + Specification Template",
        "default_evaluation_method": "Merit Point",
    },
    {
        "procurement_type": "Services - Consulting",
        "sub_type": "Consulting",
        "tender_line_basis": "Service Line (Scope / ToR)",
        "default_evaluation_method": "Merit Point",
    },
    {
        "procurement_type": "Services - Non-consulting",
        "sub_type": "Non-consulting",
        "tender_line_basis": "Service Line (Scope / ToR)",
        "default_evaluation_method": "Compliance",
    },
    {
        "procurement_type": "Works",
        "sub_type": "",
        "tender_line_basis": "BOQ Line (Work Item, Qty, Unit)",
        "default_evaluation_method": "Compliance",
    },
]

DIRECT_PURCHASE_REASONS = [
    "Spot / collection purchase",
    "Vertical integration",
    "Purchase as commission agent for another organization",
    "Via Ethiopian Commodity Exchange",
    "Commission agent purchase",
    "Negotiated purchase",
    "Contract purchase",
]

PROCUREMENT_METHODS = [
    {
        "method_name": "Open Tender",
        "who_can_bid": "Any eligible registered supplier",
        "advertised_on_portal": 1,
        "document_sale_required": 1,
        "document_sale_optional": 0,
        "number_of_envelopes": 2,
        "two_stage": 0,
        "bid_security_required": 1,
        "single_source": 0,
        "minimum_days_on_air": 21,
        "minimum_suppliers": 3,
        "default_evaluation_method": "Merit Point",
        "allowed_procurement_types": ["Goods", "Services - Consulting", "Services - Non-consulting", "Works"],
    },
    {
        "method_name": "Restricted Tender",
        "who_can_bid": "Invited only",
        "advertised_on_portal": 0,
        "document_sale_required": 0,
        "document_sale_optional": 1,
        "number_of_envelopes": 2,
        "two_stage": 0,
        "bid_security_required": 1,
        "single_source": 0,
        "minimum_days_on_air": 15,
        "minimum_suppliers": 3,
        "default_evaluation_method": "Merit Point",
        "allowed_procurement_types": ["Goods", "Services - Consulting", "Services - Non-consulting", "Works"],
    },
    {
        "method_name": "Request for Proposal",
        "who_can_bid": "Invited only",
        "advertised_on_portal": 0,
        "document_sale_required": 0,
        "document_sale_optional": 1,
        "number_of_envelopes": 2,
        "two_stage": 0,
        "bid_security_required": 0,
        "single_source": 0,
        "minimum_days_on_air": 15,
        "minimum_suppliers": 3,
        "default_evaluation_method": "Merit Point",
        "allowed_procurement_types": ["Services - Consulting", "Services - Non-consulting"],
    },
    {
        "method_name": "Two Stage Tender",
        "who_can_bid": "Any eligible registered supplier",
        "advertised_on_portal": 1,
        "document_sale_required": 1,
        "document_sale_optional": 0,
        "number_of_envelopes": 2,
        "two_stage": 1,
        "bid_security_required": 1,
        "single_source": 0,
        "minimum_days_on_air": 21,
        "minimum_suppliers": 3,
        "default_evaluation_method": "Compliance",
        "allowed_procurement_types": ["Goods", "Services - Consulting", "Services - Non-consulting", "Works"],
    },
    {
        "method_name": "Request for Quotation",
        "who_can_bid": "Invited only",
        "advertised_on_portal": 0,
        "document_sale_required": 0,
        "document_sale_optional": 0,
        "number_of_envelopes": 1,
        "two_stage": 0,
        "bid_security_required": 0,
        "single_source": 0,
        "minimum_days_on_air": 3,
        "minimum_suppliers": 3,
        "default_evaluation_method": "Lowest compliant price",
        "allowed_procurement_types": ["Goods", "Services - Consulting", "Services - Non-consulting", "Works"],
    },
    {
        "method_name": "Direct Purchase",
        "who_can_bid": "One supplier",
        "advertised_on_portal": 0,
        "document_sale_required": 0,
        "document_sale_optional": 0,
        "number_of_envelopes": 0,
        "two_stage": 0,
        "bid_security_required": 0,
        "single_source": 1,
        "minimum_days_on_air": 0,
        "minimum_suppliers": 1,
        "default_evaluation_method": "Justification + approval",
        "allowed_procurement_types": ["Goods", "Services - Consulting", "Services - Non-consulting", "Works"],
        "direct_purchase_reasons": DIRECT_PURCHASE_REASONS,
    },
]


def _upsert(doctype, name, values):
    if frappe.db.exists(doctype, name):
        doc = frappe.get_doc(doctype, name)
        _set_values(doc, values)
    else:
        doc = frappe.new_doc(doctype)
        for key, value in values.items():
            if key in ("allowed_procurement_types", "direct_purchase_reasons"):
                continue
            doc.set(key, value)
        _set_children(doc, values)
        doc.flags.ignore_permissions = True
        doc.insert(ignore_permissions=True)
        return doc
    _set_children(doc, values)
    doc.flags.ignore_permissions = True
    doc.save(ignore_permissions=True)
    return doc


def _set_values(doc, values):
    for key, value in values.items():
        if key in ("allowed_procurement_types", "direct_purchase_reasons"):
            continue
        doc.set(key, value)


def _set_children(doc, values):
    if "allowed_procurement_types" in values:
        doc.set("allowed_procurement_types", [])
        for pt in values["allowed_procurement_types"]:
            row = doc.append("allowed_procurement_types", {})
            row.procurement_type = pt

    if "direct_purchase_reasons" in values:
        doc.set("direct_purchase_reasons", [])
        for reason in values["direct_purchase_reasons"]:
            row = doc.append("direct_purchase_reasons", {})
            row.reason = reason


def _find(doctype, filters):
    return frappe.db.get_value(doctype, filters, "name")


def execute():
    if not frappe.db.exists("DocType", "Procurement Type"):
        return

    for reason in DIRECT_PURCHASE_REASONS:
        if not frappe.db.exists("Direct Purchase Reason", reason):
            doc = frappe.new_doc("Direct Purchase Reason")
            doc.reason = reason
            doc.flags.ignore_permissions = True
            doc.insert(ignore_permissions=True)

    for row in PROCUREMENT_TYPES:
        _upsert("Procurement Type", row["procurement_type"], row)

    for row in PROCUREMENT_METHODS:
        name = _find("Procurement Method", {"method_name": row["method_name"]})
        if name:
            _upsert("Procurement Method", name, row)
        else:
            doc = frappe.new_doc("Procurement Method")
            _set_values(doc, row)
            _set_children(doc, row)
            doc.flags.ignore_permissions = True
            doc.insert(ignore_permissions=True)

    frappe.db.commit()

