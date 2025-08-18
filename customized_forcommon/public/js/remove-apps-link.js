frappe.ready(() => {
    const originalToolbar = frappe.ui.toolbar.Toolbar;

    frappe.ui.toolbar.Toolbar = class extends originalToolbar {
        constructor() {
            super();
            // Remove Apps link after header is rendered
            const dropdown = document.querySelector('#toolbar-user');
            if (dropdown) {
                const appsLink = dropdown.querySelector('a[href="/apps"]');
                if (appsLink) {
                    appsLink.remove();
                }
            }
        }
    };
});
