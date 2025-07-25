$(window).on('load', function() {
    frappe.after_ajax(function () {
        $('.dropdown-help').remove();
    });
});
