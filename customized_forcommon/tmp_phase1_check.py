import frappe


def run():
    print("Procurement Types:")
    for row in frappe.get_all(
        "Procurement Type",
        fields=["name", "procurement_type", "sub_type", "tender_line_basis", "default_evaluation_method"],
    ):
        print("  ", row)

    print("Direct Purchase Reasons:")
    for row in frappe.get_all("Direct Purchase Reason", pluck="name"):
        print("  ", row)

    print("Procurement Methods:")
    for row in frappe.get_all(
        "Procurement Method",
        fields=["name", "who_can_bid", "number_of_envelopes", "advertised_on_portal", "single_source"],
    ):
        print("  ", row)

    method = frappe.get_doc("Procurement Method", "Direct Purchase")
    print("Direct Purchase reasons on method:", [r.reason for r in method.direct_purchase_reasons])
    print("Open Tender allowed types:", [r.procurement_type for r in frappe.get_doc("Procurement Method", "Open Tender").allowed_procurement_types])
