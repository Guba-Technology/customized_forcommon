setInterval(function () {

    frappe.call({
        method: "frappe.auth.get_logged_user",
        callback: function(r) {

            if (!r.message) {

                frappe.msgprint({
                    title: "Session Expired",
                    message: "You were logged out because your account was used elsewhere.",
                    indicator: "red"
                });

                setTimeout(function() {
                    if (window.customized_forcommon_clear_page_cache) {
                        window.customized_forcommon_clear_page_cache();
                    }

                    if (frappe.app && frappe.app.redirect_to_login) {
                        frappe.app.redirect_to_login();
                        return;
                    }

                    window.location.href = "/login";
                }, 2000);

            }

        }
    });

}, 2000);
