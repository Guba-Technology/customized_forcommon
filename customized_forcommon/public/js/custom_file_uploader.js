// Force execution even in production
(function() {    
    // File Uploader Customization
    if (typeof frappe !== 'undefined' && frappe.ui && frappe.ui.FileUploader) {
        const OriginalUploader = frappe.ui.FileUploader;
        
        frappe.ui.FileUploader = class CustomFileUploader extends OriginalUploader {
            constructor(opts = {}) {
                opts.disable_file_browser = true;
                opts.allow_web_link = false;
                opts.allow_take_photo = false;
                opts.allow_google_drive = false;
                opts.restrictions = opts.restrictions || {};
                opts.restrictions.allowed_file_types = [".pdf", ".jpg", ".png"];
                opts.restrictions.max_file_size = 5 * 1024 * 1024;
                super(opts);
            }
        };
    }
})();
//exist in frappe/public/js/frappe/views/pageview.js
frappe.views.pageview.with_page = function (name, callback) {
    if (frappe.standard_pages[name]) {
        if (!frappe.pages[name]) {
            frappe.standard_pages[name]();
        }
        callback();
        return;
    }

    if (
        (locals.Page && locals.Page[name] && locals.Page[name].script) ||
        name == window.page_name
    ) {
        callback();
    } else if (name) {
        //ALWAYS fetch fresh (NO localStorage)
        return frappe.call({
            method: "frappe.desk.desk_page.getpage",
            args: { name: name },
            callback: function (r) {
                callback();
            },
            freeze: true,
        });
    }
};