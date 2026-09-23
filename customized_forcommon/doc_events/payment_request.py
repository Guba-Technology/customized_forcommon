from frappe.utils import cint, flt
from erpnext.controllers.accounts_controller import (
    validate_taxes_and_charges,
    validate_inclusive_tax,
)


def apply_taxes(doc, method=None):
    initialize_taxes(doc)
    determine_exclusive_rate(doc)
    calculate_taxes(doc)


def initialize_taxes(doc):
    for tax in doc.get("custom_advance_taxes_and_charges"):
        validate_taxes_and_charges(tax)
        validate_inclusive_tax(tax, doc)

        tax_fields = [
            "total",
            "tax_fraction_for_current_item",
            "grand_total_fraction_for_current_item",
        ]

        if tax.charge_type != "Actual":
            tax_fields.append("tax_amount")

        for fieldname in tax_fields:
            tax.set(fieldname, 0.0)


def determine_exclusive_rate(doc):
    if not any(
        cint(tax.included_in_paid_amount)
        for tax in doc.get("custom_advance_taxes_and_charges")
    ):
        return

    for i, tax in enumerate(
        doc.get("custom_advance_taxes_and_charges")
    ):
        tax.tax_fraction_for_current_item = (
            get_current_tax_fraction(doc, tax)
        )

        if i == 0:
            tax.grand_total_fraction_for_current_item = (
                1 + tax.tax_fraction_for_current_item
            )
        else:
            tax.grand_total_fraction_for_current_item = (
                doc.get("custom_advance_taxes_and_charges")[i - 1]
                .grand_total_fraction_for_current_item
                + tax.tax_fraction_for_current_item
            )


def get_current_tax_fraction(doc, tax):
    current_tax_fraction = 0.0

    if cint(tax.included_in_paid_amount):
        tax_rate = tax.rate

        if tax.charge_type == "On Paid Amount":
            current_tax_fraction = tax_rate / 100.0

        elif tax.charge_type == "On Previous Row Amount":
            current_tax_fraction = (
                (tax_rate / 100.0)
                * doc.get("custom_advance_taxes_and_charges")[
                    cint(tax.row_id) - 1
                ].tax_fraction_for_current_item
            )

        elif tax.charge_type == "On Previous Row Total":
            current_tax_fraction = (
                (tax_rate / 100.0)
                * doc.get("custom_advance_taxes_and_charges")[
                    cint(tax.row_id) - 1
                ].grand_total_fraction_for_current_item
            )

    if tax.add_deduct_tax == "Deduct":
        current_tax_fraction *= -1

    return current_tax_fraction


def calculate_taxes(doc):
    doc.custom_total_taxes_and_charges = 0.0
    doc.custom_total_taxes_and_charges_company_currency = 0.0

    actual_tax_dict = {
        tax.idx: flt(
            tax.tax_amount,
            tax.precision("tax_amount"),
        )
        for tax in doc.get("custom_advance_taxes_and_charges")
        if tax.charge_type == "Actual"
    }

    for i, tax in enumerate(
        doc.get("custom_advance_taxes_and_charges")
    ):
        current_tax_amount = get_current_tax_amount(doc, tax)

        if tax.charge_type == "Actual":
            actual_tax_dict[tax.idx] -= current_tax_amount

            if (
                i
                == len(
                    doc.get("custom_advance_taxes_and_charges")
                )
                - 1
            ):
                current_tax_amount += actual_tax_dict[tax.idx]

        tax.tax_amount = current_tax_amount
        tax.base_tax_amount = current_tax_amount

        if tax.add_deduct_tax == "Deduct":
            current_tax_amount *= -1.0

        if i == 0:
            tax.total = flt(
                doc.grand_total + current_tax_amount,
                tax.precision("total"),
            )
        else:
            tax.total = flt(
                doc.get("custom_advance_taxes_and_charges")[i - 1].total
                + current_tax_amount,
                tax.precision("total"),
            )

        tax.base_total = tax.total

        doc.custom_total_taxes_and_charges += current_tax_amount
        doc.custom_total_taxes_and_charges_company_currency += (
            tax.base_tax_amount
        )


def get_current_tax_amount(doc, tax):
    tax_amount = 0.0

    if tax.charge_type == "Actual":
        tax_amount = flt(tax.tax_amount)

    elif tax.charge_type == "On Paid Amount":
        tax_amount = flt(
            doc.grand_total * tax.rate / 100
        )

    elif tax.charge_type == "On Previous Row Amount":
        previous_tax = doc.get(
            "custom_advance_taxes_and_charges"
        )[cint(tax.row_id) - 1]

        tax_amount = flt(
            previous_tax.tax_amount * tax.rate / 100
        )

    elif tax.charge_type == "On Previous Row Total":
        previous_tax = doc.get(
            "custom_advance_taxes_and_charges"
        )[cint(tax.row_id) - 1]

        tax_amount = flt(
            previous_tax.total * tax.rate / 100
        )

    return tax_amount


