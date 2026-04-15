frappe.ui.form.on("Sales Invoice", {
  validate: function (frm) {
    validate_all(frm);
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


frappe.ui.form.on("Purchase Invoice", {
  validate: function (frm) {
    // let tax_type = frm.doc.taxes.map(tax => tax.account_head || "");
    validate_all(frm);

  },


});
frappe.ui.form.on('Company', {
  onload: function (frm) {
    if (window.location.hash === "#vat_account") {
      frm.page.tabs.forEach(tab => {
        if (tab.label && tab.label.toLowerCase().includes("vat")) {
          frm.page.show_tab(tab.label);
        }
      });
    }
  }
});






function validate_all(frm) {
  let tax_type = frm.doc.taxes
    .map(tax => tax.account_head)
    .filter(head => head);
  // console.log("Filtered Tax Type List:", tax_type);

  frappe.call({
    method:
      "customized_forcommon.custom_report.my_utilities.data_validator.validate_tax_type",
    args: {
      taxes: tax_type,
    },
    callback: function (r) {
      if (!r.exec && r.message) {

        if (r.message.vat) {
          set_mandatory(frm, "vat");
        } else {
          set_free(frm, "vat");
        }
        if (r.message.withhold) {
          set_mandatory(frm, "withhold");
        } else {
          set_free(frm, "withold");
        }
        if (r.message.vat_not_exist) {

          frappe.show_alert({
            message: `
    <b style="color:red">⚠️ Unregistered VAT Account detected</b><br>
    Please enter a valid VAT Account.<br>
    You can set the account in the 
    <a href="/app/company/${encodeURIComponent(frm.doc.company)}" target="_blank">
      ${frm.doc.company}'s VAT Account Tab
    </a>.
  `,
            indicator: 'red'
          });






        }
        if (r.message.wh_not_exist) {
          // frm.set_value("custom_receipt_number", null);
          // frm.refresh_field("custom_receipt_number");
          // set_mandatory(frm, "withhold");
          frappe.show_alert({
            message: `
    <b style="color:red">⚠️ Unregistered Withhold Account detected</b><br>
    Please enter a valid Withhold Account.<br>
    You can set the account in the 
    <a href="/app/company/${encodeURIComponent(frm.doc.company)}" target="_blank">
      ${frm.doc.company}'s VAT Account Tab
    </a>.
  `,
            indicator: 'red'
          });


        }

      }
    },
  });

}





function set_mandatory(frm, element) {
  if (element == "vat") {
    frm.set_df_property("custom_vat_category", "reqd", true);
    frm.set_df_property("custom_type_of_sale", "reqd", true);
    frm.set_df_property("custom_mrc_number", "reqd", true);
    frm.set_df_property("custom_vat_receipt_number", "reqd", true);
    frm.set_df_property("custom_description", "reqd", true);
  }
  if (element == "withhold") {
    frm.set_df_property("custom_receipt_number", "reqd", true);
    frm.set_df_property("custom_withhold_date", "reqd", true);
  }

}
function set_free(frm, element) {
  if (element == "vat") {
    frm.set_df_property("custom_vat_category", "reqd", false);
    frm.set_df_property("custom_type_of_sale", "reqd", false);
    frm.set_df_property("custom_mrc_number", "reqd", false);
    frm.set_df_property("custom_vat_receipt_number", "reqd", false);
    frm.set_df_property("custom_description", "reqd", false);
  }
  if (element == "withhold") {
    frm.set_df_property("custom_receipt_number", "reqd", false);
    frm.set_df_property("custom_withhold_date", "reqd", false);
  }
}
