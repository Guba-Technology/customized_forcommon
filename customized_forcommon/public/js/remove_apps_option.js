frappe.ready(function () {
    // Find the dropdown item with the specific href attribute.
    // The "a" selector targets the anchor tag.
    // The ".dropdown-item" selector targets the class.
    // The '[href="/apps"]' selector is the most precise way to find the element.
    const appsMenuItem = document.querySelector('a.dropdown-item[href="/apps"]');

    // If the element exists, hide it and its parent container.
    // The parent element is the <li> that holds the link, hiding it removes the entire row from the dropdown.
    if (appsMenuItem) {
        appsMenuItem.parentElement.style.display = 'none';
    }
});