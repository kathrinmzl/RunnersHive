/* jshint esversion: 11 */

document.addEventListener('DOMContentLoaded', function () {
    // Select all elements with the class 'toast'
    const toastElements = document.querySelectorAll('.toast');

    // Loop through each toast element
    toastElements.forEach(function (toastEl) {
        // Initialize a new Bootstrap Toast instance for this element
        const toast = new bootstrap.Toast(toastEl);

        // Show the toast immediately
        toast.show();
    });
});
