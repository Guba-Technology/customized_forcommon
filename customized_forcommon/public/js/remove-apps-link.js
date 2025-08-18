$(document).ready(function () {
    // Observe changes in the user dropdown
    const targetNode = document.body;
    const observer = new MutationObserver(() => {
        // Remove Apps link
        $('a.dropdown-item[href="/apps"]').remove();
    });

    observer.observe(targetNode, { childList: true, subtree: true });
});
