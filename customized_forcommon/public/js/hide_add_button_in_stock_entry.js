frappe.ui.form.on("Stock Entry", {
    onload: function (frm) {
        // If any row is linked to Material Request, disable adding new rows
        if ((frm.doc.items || []).some(d => d.material_request)) {
            frm.fields_dict.items.grid.cannot_add_rows = true;
            frm.fields_dict.items.grid.cannot_add_multiple_rows = true;
        }
    },

    refresh: function (frm) {
        if ((frm.doc.items || []).some(d => d.material_request)) {
            frm.fields_dict.items.grid.cannot_add_rows = true;
            frm.fields_dict.items.grid.cannot_add_multiple_rows = true;
        } else {
            // Enable again if no material request
            frm.fields_dict.items.grid.cannot_add_rows = false;
            frm.fields_dict.items.grid.cannot_add_multiple_rows = false;
        }

        frm.fields_dict.items.refresh();
    }
});
