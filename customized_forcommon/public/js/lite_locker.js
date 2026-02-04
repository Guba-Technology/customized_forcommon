// your_app/public/js/lite_locker.js
$(document).on('app_ready', function() {
    frappe.router.on('change', () => {
        const route = frappe.get_route();
        if (!route || route.length < 2) return;

        frappe.call({
            method: "customized_forcommon.prunning.get_locked_manifest",
            callback: function(r) {
                if (!r.message) return;

                const manifest = r.message;
                const view_type = route[0]; 
                const identifier = route[1];

                if (view_type === 'Module' && manifest.modules.includes(identifier)) {
                    block_and_redirect(identifier);
                }

                else if ((view_type === 'query-report' || view_type === 'report') && manifest.reports.includes(identifier)) {
                    block_and_redirect(identifier);
                }

                else if (view_type === 'Page' && manifest.pages.includes(identifier)) {
                    block_and_redirect(identifier);
                }

                else if (view_type === 'Form' && identifier === 'DocType' && manifest.doctypes.includes(route[2])) {
                    block_and_redirect(route[2]);
                }

                else if (manifest.doctypes.includes(identifier) || manifest.modules.includes(identifier)) {
                    block_and_redirect(identifier);
                }
            }
        });
    });
});

function block_and_redirect(item) {
    frappe.show_alert({
        message: __("<b>{0}</b> is restricted in LITE mode Please contact your administrator.", [item]),
        indicator: 'red'
    }, 5);
    frappe.set_route('desk');
}