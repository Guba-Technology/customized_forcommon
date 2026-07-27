frappe.listview_settings["Project Advance Payment"] = {
    get_indicator: function (frm) {
        if (frm.status == "Open") {
            return [__("Open"), "blue", "status,=,Open"];
        } else if (frm.status == "Closed") {
            return [__("Closed"), "green", "status,=,Closed"];
        }

    }
}