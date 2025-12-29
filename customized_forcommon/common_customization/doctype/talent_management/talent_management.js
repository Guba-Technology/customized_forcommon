// Copyright (c) 2025, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("Talent Management", {
	refresh(frm) {

    if (frm.doc.status === 'Completed' && !frm.doc.__islocal) {
      frappe.call({
        method: 'customized_forcommon.common_customization.doctype.talent_management.talent_management.create_connections',
        args: { talent_doc: frm.doc.name },
        callback(r) {
          if (r.message) {
            frappe.msgprint(__('Connections created successfully'));
            frm.reload_doc();
          }
        }
      });
    }
  }
});
