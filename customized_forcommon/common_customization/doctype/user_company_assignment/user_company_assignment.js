// Copyright (c) 2025, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("User Company Assignment", {
    onload: function(frm) {
        frm.set_query("user", function() {
            return {
                query: "customized_forcommon.api.get_available_users_for_assignment"
            };
        });
    }
});
