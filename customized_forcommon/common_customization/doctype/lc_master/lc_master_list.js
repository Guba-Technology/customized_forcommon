frappe.listview_settings['LC Master'] = {
    get_indicator: function (doc) {
        if (doc.status == "Open") {
            return [__("Open"), "blue", "status,=,Open"];
        } else if (doc.status == "Closed") {
            return [__("Closed"), "green", "status,=,Closed"];
        }
    }
};