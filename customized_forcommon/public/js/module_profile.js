frappe.ui.form.on('Module Profile', {
    refresh: function (frm) {
        // List of modules you want to KEEP visible
        const allowed_modules = [
            "Accounts", "Stock", "Buying", "Selling", "HR", "Payroll",
            "Setup", "Core", "Custom", "Desk", "Email", "Automation",
            "Common Customization", "Contacts"
        ];

        // The fieldname in Module Profile is usually 'block_modules'
        // We loop through the checkboxes and hide any that aren't in our list
        $('div[data-fieldname="block_modules"] .unit-checkbox').each(function () {
            let label = $(this).text().trim();

            if (!allowed_modules.includes(label)) {
                $(this).hide();
            } else {
                $(this).show();
            }
        });
    }
});