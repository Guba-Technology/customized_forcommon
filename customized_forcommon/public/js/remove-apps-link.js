frappe.ready(() => {
    // Wait until user dropdown is rendered
    setTimeout(() => {
        // Remove "Apps" from the dropdown
        $('a.dropdown-item[data-label="Apps"]').parent().remove();
    }, 500);
});
