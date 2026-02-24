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

                const view_type = route[0];
                const identifier = route[1];
                const doc_name = route[2];

                let liteLockerExecuted = false;
                let locked_item = "";

                // 1. Module Check
                if (view_type === 'Module' && r.message.modules.includes(identifier)) {
                    liteLockerExecuted = true;
                    locked_item = identifier;
                }
                // 2. Workspace Check
                else if (view_type === 'Workspaces' && r.message.workspaces.includes(identifier)) {
                    liteLockerExecuted = true;
                    locked_item = identifier;
                }
                // 3. DocType Check (List/Form/Report)
                else if (r.message.doctypes.includes(identifier)) {
                    liteLockerExecuted = true;
                    locked_item = identifier;
                }
                // 4. Report Check
                else if (['query-report', 'report'].includes(view_type) && r.message.reports.includes(identifier)) {
                    liteLockerExecuted = true;
                    locked_item = identifier;
                }
                // 5. DocType Detail Check (e.g., viewing the DocType record itself)
                else if (view_type === 'Form' && identifier === 'DocType' && r.message.doctypes.includes(doc_name)) {
                    liteLockerExecuted = true;
                    locked_item = doc_name;
                }

                if (liteLockerExecuted) {
                    block_and_redirect(locked_item);
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