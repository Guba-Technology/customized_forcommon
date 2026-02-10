// your_app/public/js/lite_locker.js
let liteLockerExecuted = false;

$(document).on('app_ready', function () {
    frappe.router.on('change', () => {
        if (liteLockerExecuted) return;

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
    localStorage.setItem('lite_mode_redirect_active', 'true');
    localStorage.setItem('lite_mode_locked_item', item);
    window.location.href = '/app/home';
}

$(document).on('app_ready', function () {
    if (localStorage.getItem('lite_mode_redirect_active') === 'true') {
        const item = localStorage.getItem('lite_mode_locked_item') || 'requested page';

        const d = frappe.msgprint({
            title: __('Access Restricted'),
            indicator: 'red',
            message: __('The <b>{0}</b> is currently locked in LITE mode. You have been redirected to the home page.', [item]),
            primary_action: {
                label: __('Understood'),
                action: function () {
                    localStorage.removeItem('lite_mode_redirect_active');
                    localStorage.removeItem('lite_mode_locked_item');
                    d.hide();
                }
            }
        });
    }
});
