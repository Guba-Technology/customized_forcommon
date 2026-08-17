frappe.ui.form.on("Full and Final Statement", {
    refresh: function (frm) {
        // Extend the reference_document_type query filter to include your custom module
        frm.set_query("reference_document_type", "payables", function () {
            let modules = ["HR", "Payroll", "Loan Management", "Common Customization"];
            return {
                filters: {
                    istable: 0,
                    issingle: 0,
                    module: ["In", modules],
                },
            };
        });
    },
});