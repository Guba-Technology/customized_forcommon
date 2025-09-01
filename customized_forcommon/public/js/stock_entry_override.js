frappe.ui.form.on('Stock Entry', {
    onload: function (frm) {
        set_transfer_status(frm);
        toggle_item_row_add(frm);
    },

    stock_entry_type: function (frm) {
        set_transfer_status(frm);
    },

    custom_transfer_status: function (frm) {
        lock_fields_based_on_status(frm);
    },

    refresh: function (frm) {
        lock_fields_based_on_status(frm);
        toggle_item_row_add(frm);
    }
});

// --- Helpers ---
function set_transfer_status(frm) {
    if (frm.is_new()) {
        if (frm.doc.stock_entry_type === "Material Transfer") {
            frm.set_value("custom_transfer_status", "Draft");
        } else {
            frm.set_value("custom_transfer_status", null);
        }
    }
}

function toggle_item_row_add(frm) {
    const has_mr = (frm.doc.items || []).some(d => d.material_request);
    frm.fields_dict.items.grid.cannot_add_rows = has_mr;
    frm.fields_dict.items.grid.cannot_add_multiple_rows = has_mr;
    frm.fields_dict.items.refresh();
}

function lock_fields_based_on_status(frm) {
    const fields_to_lock = [
        "stock_entry_type", "outgoing_stock_entry", "purpose", "add_to_transit",
        "work_order", "purchase_order", "subcontracting_order", "delivery_note_no",
        "sales_invoice_no", "pick_list", "purchase_receipt_no", "asset_repair", "company",
        "set_posting_time", "inspection_required", "apply_putaway_rule", "from_bom",
        "use_multi_level_bom", "bom_no", "cb1", "fg_completed_qty", "get_items",
        "process_loss_percentage", "process_loss_qty", "source_warehouse_address",
        "source_address_display", "target_warehouse_address", "target_address_display",
        "sb0", "scan_barcode", "items", "get_stock_and_rate", "total_outgoing_value",
        "total_incoming_value", "value_difference", "additional_costs",
        "total_additional_costs", "contact_section", "supplier", "supplier_name",
        "supplier_address", "address_display", "accounting_dimensions_section",
        "project", "printing_settings", "select_print_heading", "letter_head",
        "is_opening", "remarks", "per_transferred", "total_amount", "job_card",
        "amended_from", "credit_note", "is_return", "custom_transit_warehouse",
        "custom_employee", "custom_work_order"
    ];

    if (["In Transit", "Completed"].includes(frm.doc.custom_transfer_status)) {
        fields_to_lock.forEach(f => frm.set_df_property(f, "read_only", 1));
        frm.toggle_enable("posting_date", false);
        frm.toggle_enable("posting_time", false);
        frm.set_df_property("from_warehouse", "read_only", 1);
        frm.set_df_property("to_warehouse", "read_only", 1);
        frm.disable_save();
    } else {
        fields_to_lock.forEach(f => frm.set_df_property(f, "read_only", 0));
        frm.toggle_enable("posting_date", true);
        frm.toggle_enable("posting_time", true);
        frm.set_df_property("from_warehouse", "read_only", 0);
        frm.set_df_property("to_warehouse", "read_only", 0);
        frm.enable_save();
    }
}
