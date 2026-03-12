// Copyright (c) 2026, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance Collection Log", {
	refresh: function(frm) {
        if (!frm.is_new()) {
            frm.disable_save(); 
            frm.set_read_only(); 
        }
    }
});
