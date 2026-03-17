frappe.msgprint_original = frappe.msgprint;

frappe.msgprint = function(msg, title, is_minimizable) {
    if (typeof msg === "string" && msg.includes("does not have doctype access via role permission")) {
        msg = `
            <div style="font-weight: bold;">
                You do not have permission to access this document.<br>
                Please contact your system administrator.
            </div>
        `;
    }

    return frappe.msgprint_original(msg, title, is_minimizable);
};