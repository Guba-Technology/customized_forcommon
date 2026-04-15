frappe.ui.form.on("Sales Order", {
    validate: function (frm) {
        calculate_all(frm);
    },

});
frappe.ui.form.on('Sales Taxes and Charges', {
    rate(frm) {
        calculate_all(frm);
    },
    charge_type(frm) {
        calculate_all(frm);
    },
    taxes_add(frm) {
        calculate_all(frm);
    },
    taxes_remove(frm) {
        calculate_all(frm);
    }
});
// MAIN FUNCTION
async function calculate_all(frm) {

    let factory_share_total = 0;

    // 1️⃣ Calculate Factory Share Total
    for (let item of (frm.doc.items || [])) {

        if (!item.item_code) continue;

        let r = await frappe.db.get_value(
            "Item",
            item.item_code,
            "custom_factory_share_amount"
        );

        let fs = (r.message.custom_factory_share_amount || 0) * (item.qty || 0);
        factory_share_total += fs;
    }

    frm.set_value("custom_factory_share_total", factory_share_total);

    // 2️⃣ Apply Taxes
    let total_taxes = 0;
    let running_total = frm.doc.net_total || 0;

    (frm.doc.taxes || []).forEach(row => {

        // 🔹 On Factory Share
        if (row.charge_type === "On Factory Share") {

            row.tax_amount = (factory_share_total * (row.rate || 0)) / 100;

        }

        // 🔹 SIDF
        if (row.charge_type === "SIDF") {

            row.rate = 0;
            row.tax_amount = (frm.doc.net_total || 0) - factory_share_total;

        }

        // accumulate
        running_total += row.tax_amount || 0;

        row.total = running_total;
        total_taxes += row.tax_amount || 0;
    });

    // 3️⃣ Update totals
    frm.set_value("total_taxes_and_charges", total_taxes);
    frm.set_value("base_total_taxes_and_charges", total_taxes);

    frm.refresh_field("taxes");
}






