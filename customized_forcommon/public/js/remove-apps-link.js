frappe.ready(() => {
    const removeAppsLink = () => {
        const userDropdown = document.querySelector('#toolbar-user');
        if (userDropdown) {
            const appsLink = userDropdown.querySelector('a[href="/apps"]');
            if (appsLink) appsLink.remove();
        }
    };

    // Remove Apps link after toolbar first renders
    removeAppsLink();

    // Remove Apps link every time page changes (toolbar re-renders)
    $(document).on('page-change', () => {
        removeAppsLink();
    });
});
