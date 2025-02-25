//--------------------------------------//
//       static/js/auth/index.js        //
//--------------------------------------//

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  modal.classList.add("hidden");
}

function showLoadingOverlay(show) {
  const overlay = document.getElementById("loading-overlay");
  if (show) {
    overlay.classList.remove("hidden");
  } else {
    overlay.classList.add("hidden");
  }
}

/**
 * Retrieve CSRF token from meta tag (Flask-WTF places it there)
 */
function getCSRFToken() {
  const metaTag = document.querySelector("meta[name='csrf-token']");
  return metaTag ? metaTag.getAttribute("content") : "";
}
