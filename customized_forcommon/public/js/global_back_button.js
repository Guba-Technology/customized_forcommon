// Back Button Injection Script
frappe.provide("frappe.ui");

$(document).ready(() => {
    inject_back_button();
});

frappe.router.on('change', () => {
    const checkInterval = setInterval(() => {
        if (inject_back_button()) {
            clearInterval(checkInterval);
        }
    }, 100);
    setTimeout(() => clearInterval(checkInterval), 2000);
});

function inject_back_button() {
    if ($(".page-head:visible .btn-global-back").length > 0) {
        return true; 
    }

    let $page_head = $(".page-head:visible");
    if ($page_head.length === 0) return false;

    let $target = $page_head.find(".title-area, .breadcrumb-container").first();

    if ($target.length === 0) {
        $target = $page_head.find(".standard-actions, .page-actions").first();
    }

    if ($target.length > 0) {
        const back_btn = `
    <button class="btn btn-sm btn-secondary btn-global-back" 
            title="${__("Go Back")}"
            style="
                margin-right: 12px; 
                display: inline-flex; 
                align-items: center; 
                justify-content: center; 
                height: 28px; 
                padding: 0 8px; 
                border-radius: 6px;
                background-color: #ffffff;
                border: 1px solid var(--border-color);
            ">
        <svg class="icon icon-sm" style="stroke: #0a66b1; fill: #0a66b1; margin-right: 4px;">
            <use href="#icon-arrow-left"></use>
        </svg>
        <span style="color: #0a66b1; font-weight: 500;">Back</span>
    </button>
`;

        const $btn = $(back_btn);
        $target.prepend($btn);

        $btn.on("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
            if (window.history.length > 1) {
                window.history.back();
            } else {
                frappe.set_route("desk");
            }
        });

        return true; 
    }

    return false; 
}
