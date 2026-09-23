frappe.ui.form.on("Payment Request", {
    refresh(frm) {
        frm.fields_dict.custom_advance_taxes_and_charges.grid.grid_rows.forEach(
            (grid_row) => {
                grid_row.toggle_editable(
                    "tax_amount",
                    grid_row.doc.charge_type === "Actual"
                );
            }
        );
    },
    setup(frm) {
        frm.set_query("custom_sales_taxes_and_charges_template", function () {
            return {
                filters: {
                    company: frm.doc.company,
                    disabled: false,
                },
            };
        });

        frm.set_query("custom_purchase_taxes_and_charges_template", function () {
            return {
                filters: {
                    company: frm.doc.company,
                    disabled: false,
                },
            };
        });
    },

    custom_sales_taxes_and_charges_template: function (frm) {
        frm.trigger("fetch_taxes_from_template");
    },

    custom_purchase_taxes_and_charges_template: function (frm) {
        frm.trigger("fetch_taxes_from_template");
    },

    fetch_taxes_from_template: function (frm) {
        let master_doctype = "";
        let taxes_and_charges = "";

        if (frm.doc.party_type == "Supplier") {
            master_doctype = "Purchase Taxes and Charges Template";
            taxes_and_charges = frm.doc.custom_purchase_taxes_and_charges_template;
        } else if (frm.doc.party_type == "Customer") {
            master_doctype = "Sales Taxes and Charges Template";
            taxes_and_charges = frm.doc.custom_sales_taxes_and_charges_template;
        }

        if (!taxes_and_charges) {
            return;
        }

        frappe.call({
            method: "erpnext.controllers.accounts_controller.get_taxes_and_charges",
            args: {
                master_doctype: master_doctype,
                master_name: taxes_and_charges,
            },
            callback: function (r) {
                if (!r.exc && r.message) {
                    for (let tax of r.message) {
                        if (tax.charge_type === "On Net Total") {
                            tax.charge_type = "On Paid Amount";
                        }
                        frm.add_child(
                            "custom_advance_taxes_and_charges",
                            tax
                        );
                    }

                    frm.events.apply_taxes(frm);

                    frm.refresh_field(
                        "custom_advance_taxes_and_charges"
                    );
                }
            },
        });
    },

    apply_taxes: function (frm) {
        frm.events.initialize_taxes(frm);
        frm.events.determine_exclusive_rate(frm);
        frm.events.calculate_taxes(frm);
    },

    initialize_taxes: function (frm) {
        $.each(
            frm.doc["custom_advance_taxes_and_charges"] || [],
            function (i, tax) {
                frm.events.validate_taxes_and_charges(tax);
                frm.events.validate_inclusive_tax(tax);

                let tax_fields = [
                    "total",
                    "tax_fraction_for_current_item",
                    "grand_total_fraction_for_current_item",
                ];

                if (cstr(tax.charge_type) != "Actual") {
                    tax_fields.push("tax_amount");
                }

                $.each(tax_fields, function (i, fieldname) {
                    tax[fieldname] = 0.0;
                });
            }
        );
    },

    validate_taxes_and_charges: function (tax) {
        if (tax.account_head && !tax.description) {
            tax.description = tax.account_head.split(" - ")[0];
        }
    },

    validate_inclusive_tax: function (tax) {
        if (tax.included_in_paid_amount && tax.charge_type == "Actual") {
            tax.included_in_paid_amount = 0;
        }
    },

    determine_exclusive_rate: function (frm) {
        let has_inclusive_tax = false;

        $.each(
            frm.doc["custom_advance_taxes_and_charges"] || [],
            function (i, tax) {
                if (cint(tax.included_in_paid_amount)) {
                    has_inclusive_tax = true;
                }
            }
        );

        if (has_inclusive_tax == false) {
            return;
        }

        let cumulated_tax_fraction = 0.0;

        $.each(
            frm.doc["custom_advance_taxes_and_charges"] || [],
            function (i, tax) {
                tax.tax_fraction_for_current_item =
                    frm.events.get_current_tax_fraction(frm, tax);

                if (i == 0) {
                    tax.grand_total_fraction_for_current_item =
                        1 + tax.tax_fraction_for_current_item;
                } else {
                    tax.grand_total_fraction_for_current_item =
                        frm.doc[
                            "custom_advance_taxes_and_charges"
                        ][i - 1].grand_total_fraction_for_current_item +
                        tax.tax_fraction_for_current_item;
                }

                cumulated_tax_fraction +=
                    tax.tax_fraction_for_current_item;
            }
        );
    },

    get_current_tax_fraction: function (frm, tax) {
        let current_tax_fraction = 0.0;

        if (cint(tax.included_in_paid_amount)) {
            let tax_rate = tax.rate;

            if (tax.charge_type == "On Paid Amount") {
                current_tax_fraction = tax_rate / 100.0;
            } else if (tax.charge_type == "On Previous Row Amount") {
                current_tax_fraction =
                    (tax_rate / 100.0) *
                    frm.doc["custom_advance_taxes_and_charges"][
                        cint(tax.row_id) - 1
                    ].tax_fraction_for_current_item;
            } else if (tax.charge_type == "On Previous Row Total") {
                current_tax_fraction =
                    (tax_rate / 100.0) *
                    frm.doc["custom_advance_taxes_and_charges"][
                        cint(tax.row_id) - 1
                    ].grand_total_fraction_for_current_item;
            }
        }

        if (tax.add_deduct_tax && tax.add_deduct_tax == "Deduct") {
            current_tax_fraction *= -1;
        }

        return current_tax_fraction;
    },

    calculate_taxes: function (frm) {
        frm.doc.custom_total_taxes_and_charges = 0.0;
        frm.doc.custom_total_taxes_and_charges_company_currency = 0.0;

        let actual_tax_dict = {};

        $.each(
            frm.doc["custom_advance_taxes_and_charges"] || [],
            function (i, tax) {
                if (tax.charge_type == "Actual") {
                    actual_tax_dict[tax.idx] = flt(
                        tax.tax_amount,
                        precision("tax_amount", tax)
                    );
                }
            }
        );

        $.each(
            frm.doc["custom_advance_taxes_and_charges"] || [],
            function (i, tax) {
                let current_tax_amount =
                    frm.events.get_current_tax_amount(frm, tax);

                if (tax.charge_type == "Actual") {
                    actual_tax_dict[tax.idx] -= current_tax_amount;

                    if (
                        i ==
                        frm.doc["custom_advance_taxes_and_charges"].length - 1
                    ) {
                        current_tax_amount += actual_tax_dict[tax.idx];
                    }
                }

                tax.tax_amount = current_tax_amount;
                tax.base_tax_amount = current_tax_amount;

                if (tax.add_deduct_tax == "Deduct") {
                    current_tax_amount *= -1.0;
                }

                if (i == 0) {
                    tax.total = flt(
                        frm.doc.grand_total + current_tax_amount,
                        precision("total", tax)
                    );
                } else {
                    tax.total = flt(
                        frm.doc[
                            "custom_advance_taxes_and_charges"
                        ][i - 1].total + current_tax_amount,
                        precision("total", tax)
                    );
                }

                tax.base_total = tax.total;

                frm.doc.custom_total_taxes_and_charges +=
                    current_tax_amount;

                frm.doc.custom_total_taxes_and_charges_company_currency +=
                    tax.base_tax_amount;
            }
        );

        frm.refresh_field("custom_advance_taxes_and_charges");
        frm.refresh_field("custom_total_taxes_and_charges");
        frm.refresh_field(
            "custom_total_taxes_and_charges_company_currency"
        );
    },

    get_current_tax_amount: function (frm, tax) {
        let tax_amount = 0.0;

        if (tax.charge_type == "Actual") {
            tax_amount = flt(tax.tax_amount);
        } else if (tax.charge_type == "On Paid Amount") {
            tax_amount = flt(
                frm.doc.grand_total * tax.rate / 100
            );
        } else if (tax.charge_type == "On Previous Row Amount") {
            let previous_tax =
                frm.doc["custom_advance_taxes_and_charges"][
                cint(tax.row_id) - 1
                ];

            tax_amount = flt(
                previous_tax.tax_amount * tax.rate / 100
            );
        } else if (tax.charge_type == "On Previous Row Total") {
            let previous_tax =
                frm.doc["custom_advance_taxes_and_charges"][
                cint(tax.row_id) - 1
                ];

            tax_amount = flt(
                previous_tax.total * tax.rate / 100
            );
        }

        return tax_amount;
    },
});


frappe.ui.form.on("Advance Taxes and Charges", {

    rate: function (frm) {
        frm.events.apply_taxes(frm);
    },

    tax_amount: function (frm) {
        frm.events.apply_taxes(frm);
    },

    row_id: function (frm) {
        frm.events.apply_taxes(frm);
    },

    taxes_remove: function (frm) {
        frm.events.apply_taxes(frm);
    },

    included_in_paid_amount: function (frm) {
        frm.events.apply_taxes(frm);
    },

    charge_type(frm, cdt, cdn) {
        const row = frappe.get_doc(cdt, cdn);
        const grid_row =
            frm.fields_dict.custom_advance_taxes_and_charges.grid.get_row(cdn);

        grid_row.toggle_editable(
            "tax_amount",
            row.charge_type === "Actual"
        );

        frm.events.apply_taxes(frm);
    },
});
