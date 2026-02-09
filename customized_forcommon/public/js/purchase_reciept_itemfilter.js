frappe.ui.form.on("Purchase Receipt", {
    onload(frm) {
        set_pr_item_filter(frm);
    },
    refresh(frm) {
        set_pr_item_filter(frm);
    }
});

frappe.ui.form.on("Purchase Receipt Item", {
    warehouse(frm, cdt, cdn) {
        set_pr_item_filter(frm);
    }
});

function set_pr_item_filter(frm) {
    frm.fields_dict.items.grid.get_field("item_code").get_query = function (doc, cdt, cdn) {
        let row = locals[cdt][cdn];
        let warehouse = row.warehouse; // Accepted Warehouse

        if (!warehouse) {
            frappe.msgprint("Please select Accepted Warehouse first");
            return {};
        }

        return {
            query: "customized_forcommon.item_queries.get_items_by_warehouse",
            filters: {
                warehouse: warehouse
            }
        };
    };

    frm.refresh_field("items");
}
