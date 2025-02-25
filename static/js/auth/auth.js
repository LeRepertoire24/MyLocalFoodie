// static/js/auth/auth.js

document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  const payrollIdInput = document.getElementById("payroll-id");
  const passwordInput = document.getElementById("password");
  const loginButton = document.getElementById("login-submit-btn");
  const loginErrors = document.getElementById("login-errors").querySelector("p");
  const loginErrorsContainer = document.getElementById("login-errors");
  
  const validateForm = () => {
    // Basic checks for empty fields
    const payrollIdValid = payrollIdInput.value.trim() !== "";
    const passwordValid = passwordInput.value.trim().length >= 8;
    loginButton.disabled = !(payrollIdValid && passwordValid);
  };

  // Validate on input
  payrollIdInput.addEventListener("input", validateForm);
  passwordInput.addEventListener("input", validateForm);

  // Handle submit
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    loginErrorsContainer.classList.add("hidden");
    loginErrors.textContent = "";

    // Show loading overlay (optional)
    showLoadingOverlay(true);

    try {
      const response = await fetch("/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(), // from index.js utility
        },
        body: JSON.stringify({
          payroll_id: payrollIdInput.value.trim(),
          password: passwordInput.value.trim()
        }),
      });

      const data = await response.json();

      if (!data.success) {
        // Show error message
        loginErrorsContainer.classList.remove("hidden");
        loginErrors.textContent = data.error || "Login failed. Please try again.";
      } else {
        // Redirect on success
        window.location.href = data.redirect_url;
      }
    } catch (error) {
      loginErrorsContainer.classList.remove("hidden");
      loginErrors.textContent = "An unexpected error occurred. Please try again.";
      console.error("Login error:", error);
    } finally {
      showLoadingOverlay(false);
    }
  });
});
