// Copyright (c) 2026, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("Material Receipt for Transfer", {
    refresh: function (frm) {
        const form_fields = ["items", "remark_list", "total_rejected_quantity"];

        frm.fields_dict && Object.keys(frm.fields_dict).forEach(fieldname => {
            if (!form_fields.includes(fieldname)) {
                frm.set_df_property(fieldname, "read_only", 1);
            }
        });
    }
});
