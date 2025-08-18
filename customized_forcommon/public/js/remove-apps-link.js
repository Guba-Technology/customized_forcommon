frappe.ready(() => {
    if (frappe.boot.navbar_settings && frappe.boot.navbar_settings.settings_dropdown) {
        frappe.boot.navbar_settings.settings_dropdown = frappe.boot.navbar_settings.settings_dropdown.filter(item => item.route !== '/apps');
    }
});
