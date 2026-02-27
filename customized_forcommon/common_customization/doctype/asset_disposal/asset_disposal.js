// Copyright (c) 2025, guba and contributors
// For license information, please see license.txt

frappe.ui.form.on("Asset Disposal", {
	// refresh(frm) {

	// },

setup: function(frm){
    frm.set_query("buyer_reciever", function() {
        return {
            filters: {
                name: ["in",["Customer","Supplier"]],
            }
        }
    })
},
buyer_reciever: function(frm)
{
    frm.set_df_property("buyer","label", frm.doc.buyer_reciever);
    frm.set_value("buyer", "");
},
salvage_value: function(frm)
{
    frappe.call({
        method: "customized_forcommon.common_customization.doctype.asset_disposal.asset_disposal.calculate_gain_loss",
        args: {
            "doc": frm.doc.asset,
            "salvage_value": frm.doc.salvage_value
        },
        callback: function(r) {
            if (r.message) {
                frm.set_value("gain_loss", r.message.gain_loss);
                frm.refresh_field("gain_loss");
            }
        }
    })
    frm.set_value("gain_loss", frm.doc.salvage_value);
},
// onsubmit: function(frm) {
   before_submit: function(frm) {
	if (frm.doc.disposal_type == "Scrap") {
        frappe.confirm(__("Do you really want to scrap this asset?"), function () {
		frappe.call({
			args: {
				asset_name: frm.doc.asset,
			},
			method: "erpnext.assets.doctype.asset.depreciation.scrap_asset",
			callback: function (r) {
				cur_frm.reload_doc();
			},
		});
	});
    }

    if (frm.doc.disposal_type == "Sale") {
       frappe.confirm(__("Do you really want to sell this asset?"), function () {
           var asset = frm.doc.asset;
        frappe.call({
      method: "customized_forcommon.common_customization.doctype.asset_disposal.asset_disposal.get_asset_data",
      args: {
        doc: asset,
        
      },
      callback: function(r) {
        if (r.message) {
        

        frappe.call({
			args: {
				asset: asset,
				item_code: r.message.item_code,
				company: r.message.company,
				serial_no: "",
			},
			method: "erpnext.assets.doctype.asset.asset.make_sales_invoice",
			callback: function (r) {
				var doclist = frappe.model.sync(r.message);
				frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
			},
		});
            
        }
      },
        });
                   

       
       }) 

    }

}
});



