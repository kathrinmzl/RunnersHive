/* jshint esversion: 11 */

document.addEventListener("DOMContentLoaded", function () {
    const collapseEl = document.getElementById("eventFilters");
    const button = document.getElementById("filterToggleBtn");

    // When the collapse opens
    collapseEl.addEventListener("show.bs.collapse", () => {
        button.innerHTML = "Filter Events ▴";  // Up arrow
    });

    // When the collapse closes
    collapseEl.addEventListener("hide.bs.collapse", () => {
        button.innerHTML = "Filter Events ▾";  // Down arrow
    });
});