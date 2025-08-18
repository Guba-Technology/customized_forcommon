frappe.ready(() => {
    // Observe the body for changes
    const observer = new MutationObserver(() => {
        // Remove the Apps link by href
        const appsLink = document.querySelector('a.dropdown-item[href="/apps"]');
        if (appsLink) {
            appsLink.remove();
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
});
