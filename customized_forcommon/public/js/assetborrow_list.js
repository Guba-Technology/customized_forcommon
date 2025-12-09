//Why it separate from asset.js b/c when put that when refresh remove the custom status
frappe.listview_settings['Asset Borrowing'] = {
    get_indicator: function(doc) {
        if(doc.status == "Borrowed") {
            return [__("Borrowed"), "orange", "status,=,Borrowed"];
        }
    }
};