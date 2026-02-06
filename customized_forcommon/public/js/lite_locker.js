// your_app/public/js/lite_locker.js
let liteLockerExecuted = false;  // guard flag

$(document).on('app_ready', function () {
    frappe.router.on('change', () => {
        if (liteLockerExecuted) return;  // prevent rerun

        const route = frappe.get_route();
        if (!route || route.length < 2) return;

        frappe.call({
            method: "customized_forcommon.prunning.get_locked_manifest",
            callback: function (r) {
                if (!r.message) return;

                const manifest = r.message;
                const view_type = route[0];
                const identifier = route[1];

                if (view_type === 'Module' && manifest.modules.includes(identifier)) {
                    block_and_redirect(identifier);
                    liteLockerExecuted = true;
                }

                else if ((view_type === 'query-report' || view_type === 'report') && manifest.reports.includes(identifier)) {
                    block_and_redirect(identifier);
                    liteLockerExecuted = true;
                }

                else if (view_type === 'Page' && manifest.pages.includes(identifier)) {
                    block_and_redirect(identifier);
                    liteLockerExecuted = true;
                }

                else if (view_type === 'Form' && identifier === 'DocType' && manifest.doctypes.includes(route[2])) {
                    block_and_redirect(route[2]);
                    liteLockerExecuted = true;
                }

                else if (manifest.doctypes.includes(identifier) || manifest.modules.includes(identifier)) {
                    block_and_redirect(identifier);
                    liteLockerExecuted = true;
                }
            }
        });
    });
});

function block_and_redirect(item) {
    frappe.msgprint({
        title: __('Access Restricted'),
        message: __('The {0} is currently locked in LITE mode. You will be redirected to the home page.', [item]),
        indicator: 'red'
    });
    setTimeout(() => {
        window.location.href = '/app/home';
    }, 3000);
}
