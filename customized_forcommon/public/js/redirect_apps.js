frappe.ready(() => {
    if (window.location.pathname === "/apps") {
        window.location.replace("/app/home");
    }
});
