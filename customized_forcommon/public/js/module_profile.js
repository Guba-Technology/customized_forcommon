frappe.ui.form.on('Module Profile', {
    refresh: function (frm) {
        // List of modules you want to KEEP visible
        const allowed_modules = [
            "CRM", "Stock", "HR", "Support", "Assets", "Quality Management",
            "Setup", "Core", "Social", "Desk", "Email", "Automation", "Contacts", "Custom", "Printing",
            "Workflow", "Integrations", "Website",
            "Blood Bank Customization", "Document Managing", "Overtime Management",
            "Ethiopian Calendar"
        ];

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