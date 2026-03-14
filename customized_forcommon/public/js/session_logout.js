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
                    window.location.href = "/login";
                }, 2000);

            }

        }
    });

}, 2000);