frappe.ui.form.on('Auto Repeat', {
    onload: function(frm) {
        if (frm.is_new()) {
            let ref_doc = frm.doc.reference_document;
            if (!ref_doc && frappe.route_options && frappe.route_options.reference_document) {
                ref_doc = frappe.route_options.reference_document;
            }

            if (!ref_doc) {
                const last_route = frappe.get_prev_route();
                if (last_route && last_route[1] === 'Quotation') {
                    ref_doc = last_route[2];
                }
            }
            if (ref_doc && ref_doc.startsWith("SAL-QTN-")) {
                frm.set_value("reference_doctype", "Quotation");

                setTimeout(() => {
                    frm.set_value("reference_document", ref_doc);
                    frm.refresh_field("reference_document");
                    
                    frappe.route_options = null;
                }, 200);
            }
        }
    }
});