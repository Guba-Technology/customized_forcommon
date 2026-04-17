// Copyright (c) 2026, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("LC Master", {
    refresh(frm) {
        setup_lc_tables(frm);
    }
});

function setup_lc_tables(frm) {

    // PURCHASE ORDERS TABLE
    frm.fields_dict.linked_purchase_orders.grid.get_field("doc_name").get_query = function () {
        return {
            filters: {
                docstatus: 1
            }
        };
    };

    frappe.ui.form.on("LC Linked Document", {
        linked_purchase_orders_add(frm, cdt, cdn) {
            let row = locals[cdt][cdn];
            row.doc_type = "Purchase Order";
            frm.refresh_field("linked_purchase_orders");
        }
    });

    // PURCHASE INVOICE TABLE
    frm.fields_dict.linked_purchase_invoices.grid.get_field("doc_name").get_query = function () {
        return {
            filters: {
                docstatus: 1
            }
        };
    };

    frappe.ui.form.on("LC Linked Document", {
        linked_purchase_invoices_add(frm, cdt, cdn) {
            let row = locals[cdt][cdn];
            row.doc_type = "Purchase Invoice";
            frm.refresh_field("linked_purchase_invoices");
        }
    });
}