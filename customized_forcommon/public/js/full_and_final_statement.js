frappe.ui.form.on("Full and Final Statement", {
    refresh: function (frm) {
        // 1. Allow custom module in document type selection
        frm.events.set_queries(frm, "payables");
        frm.events.set_queries(frm, "receivables");
    },

    set_queries: function (frm, type) {
        frm.set_query("reference_document_type", type, function () {
            let modules = ["HR", "Payroll", "Loan Management", "Common Customization"];
            return {
                filters: {
                    istable: 0,
                    issingle: 0,
                    module: ["In", modules],
                },
            };
        });

        frm.set_query("reference_document", type, function (doc, cdt, cdn) {
            let fnf_doc = frappe.get_doc(cdt, cdn);
            // Crucial: Initialize filters inside callback so previous filters do not bleed through
            let filters = {};

            frappe.model.with_doctype(fnf_doc.reference_document_type, function () {
                if (frappe.model.is_tree(fnf_doc.reference_document_type)) {
                    filters["is_group"] = 0;
                }

                if (frappe.model.is_submittable(fnf_doc.reference_document_type)) {
                    filters["docstatus"] = ["!=", 2];
                }

                if (frappe.meta.has_field(fnf_doc.reference_document_type, "company")) {
                    filters["company"] = frm.doc.company;
                }

                if (frappe.meta.has_field(fnf_doc.reference_document_type, "employee")) {
                    filters["employee"] = frm.doc.employee;
                }

                // Add DocType-specific filters only when selected
                if (fnf_doc.reference_document_type === "Leave Encashment") {
                    filters["status"] = "Unpaid";
                    filters["pay_via_payment_entry"] = 1;
                }
            });

            return {
                filters: filters,
            };
        });
    },
});