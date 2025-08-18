$(window).on('load', function () {
    frappe.after_ajax(function () {
        // Remove the Apps link from the user dropdown
        $('a.dropdown-item[href="/apps"]').remove();
    });
});
