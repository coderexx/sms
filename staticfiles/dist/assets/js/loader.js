// Show loader on page load or navigation
function showLoader() {
document.getElementById("loader").classList.remove("d-none");
}

// Hide loader when page is fully loaded
function hideLoader() {
document.getElementById("loader").classList.add("d-none");
}

// Show loader when the page is reloaded or navigated to
window.addEventListener("beforeunload", function () {
showLoader(); // Show loader when leaving the page
});

// Hide the loader when the page is loaded
window.addEventListener("load", function () {
hideLoader(); // Hide loader when page fully loads
});

// Detect when the visibility of the page changes (e.g., after navigating)
document.addEventListener("visibilitychange", function () {
if (document.visibilityState === "hidden") {
    showLoader(); // Show loader when navigating away
} else {
    hideLoader(); // Hide loader when the page is visible again
}
});

// Handle back/forward navigation (popstate event)
window.addEventListener("popstate", function () {
showLoader(); // Show loader when navigating back/forward
setTimeout(() => {
    hideLoader(); // Hide loader after a brief delay (let the page load)
}, 100); // Adjust delay if necessary to match your needs
});