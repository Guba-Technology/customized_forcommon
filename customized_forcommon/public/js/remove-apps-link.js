frappe.ready(() => {
    // Listen for dropdown opening
    $(document).on('click', '#toolbar-user', function () {
        const dropdown = document.querySelector('#toolbar-user');
        if (dropdown) {
            const appsLink = dropdown.querySelector('a[href="/apps"]');
            if (appsLink) {
                appsLink.remove();
            }
        }
    });
});
