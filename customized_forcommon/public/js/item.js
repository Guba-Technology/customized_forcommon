frappe.ui.form.on("Item", {
    refresh: function(frm) {
        render_qr_image_in_html_field(frm);
    },
    custom_qr_code: function(frm) {
        render_qr_image_in_html_field(frm);
    }
});

function render_qr_image_in_html_field(frm) {
    if (frm.doc.custom_qr_code) {
        let html_content = `
            <div style="text-align: center; padding: 10px; border: 1px solid #d1d8dd; border-radius: 4px; background-color: #f8f9fa;">
                <img src="${frm.doc.custom_qr_code}" style="max-width: 200px; height: auto; border: 1px solid #eee;" 
                     onerror="this.parentElement.innerHTML='<p>Image not found</p>';" />
                <div style="margin-top: 8px; font-weight: bold; color: #555;">Item QR Code</div>
            </div>
        `;
        frm.set_df_property("custom_qr_image", "options", html_content);
        frm.refresh_field("custom_qr_image");
    } else {
        frm.set_df_property("custom_qr_image", "options", "<p style='text-align:center;'>No QR Code attached yet.</p>");
    }
}

//     after_save: function(frm) {
//         // Triggered after the save button is clicked
//         generate_item_codes(frm);
//     },
    
//     on_update: function(frm) {
//         // Triggered after the document is updated in the DB
//         // Useful if you are updating via scripts or API
//         render_qr_html(frm);
//     },

//     refresh: function(frm) {
//         // Render the image when the form loads
//         render_qr_html(frm);
//     }
// });

// function generate_item_codes(frm) {
//     if (frm.doc.item_code) {
//         frappe.call({
//             method: "customized_forcommon.overrides.item.generate_qr_code",
//             args: {
//                 name: frm.doc.name,
//             },
//             callback: function(r) {
//                 if (r.message) {
//                     // Update the HTML field directly with an <img> tag
//                     frm.doc.custom_qrcode = r.message;
//                     render_qr_html(frm);
//                 }
//             }
//         });
//     }
// }

// function render_qr_html(frm) {
//     if (frm.doc.custom_qrcode) {
//         // Set the HTML field to display the image from the disk path
//         let html_content = `
//             <div style="text-align: center; padding: 10px; border: 1px solid #d1d8dd; border-radius: 4px;">
//                 <img src="${frm.doc.custom_qrcode}" style="max-width: 200px; height: auto;" />
//                 <div style="margin-top: 5px; font-weight: bold;">Item QR Code</div>
//             </div>
//         `;
//         frm.set_df_property("custom_qr_code", "options", html_content);
//     }
// }