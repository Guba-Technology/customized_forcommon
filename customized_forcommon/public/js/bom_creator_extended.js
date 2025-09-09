// File: customized_forcommon/public/js/bom_creator_extended.js
frappe.provide("frappe.ui.form.BOMCreator");

frappe.ui.form.BOMCreator.make_new_entry = function(frm) {
    if (!frm._bom_creator_dialog) {
        frm._bom_creator_dialog = new frappe.ui.Dialog({
            title: __("Multi-level BOM Creator"),
            fields: [
                { label: __("Name"), fieldtype: "Data", fieldname: "name", reqd: 1 },
                { fieldtype: "Column Break" },
                { label: __("Company"), fieldtype: "Link", fieldname: "company", options: "Company", reqd: 1, default: frappe.defaults.get_user_default("Company") },
                { fieldtype: "Section Break" },
                { label: __("Item Code (Final Product)"), fieldtype: "Link", fieldname: "item_code", options: "Item", reqd: 1 },
                { fieldtype: "Column Break" },
                { label: __("Quantity"), fieldtype: "Float", fieldname: "qty", reqd: 1, default: 1.0 },
                { fieldtype: "Section Break" },
                { label: __("Currency"), fieldtype: "Link", fieldname: "currency", options: "Currency", reqd: 1, default: frappe.defaults.get_global_default("currency") },
                { fieldtype: "Column Break" },
                { label: __("Conversion Rate"), fieldtype: "Float", fieldname: "conversion_rate", reqd: 1, default: 1.0 },
                { fieldtype: "Section Break", label: __("Additional Settings") },
                { label: __("Routing"), fieldtype: "Link", fieldname: "routing", options: "Routing" },
            ],
            primary_action_label: __("Create"),
            primary_action: (values) => {
                values.doctype = frm.doc.doctype;
                frappe.db.insert(values).then((doc) => {
                    frappe.set_route("Form", doc.doctype, doc.name);
                    frm._bom_creator_dialog.clear();
                }).catch((err) => {
                    frappe.msgprint({
                        title: __("Error"),
                        message: err.message || __("Failed to create BOM"),
                        indicator: "red",
                    });
                });
            }
        });
        frm._bom_creator_dialog.fields_dict.item_code.get_query = "erpnext.controllers.queries.item_query";
    }

    frm._bom_creator_dialog.show();
};
