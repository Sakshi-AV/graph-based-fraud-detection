import { postJson } from "../api.js";
import { setText } from "../utils.js";

export function initAuthPage() {
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const toggleAdminBtn = document.getElementById("toggleAdminBtn");
  const loginTitle = document.getElementById("loginTitle");
  const loginType = document.getElementById("loginType");

  const tabs = document.querySelectorAll(".auth-tab");

  // Tab switching
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".auth-form").forEach(f => f.classList.remove("active"));
      
      tab.classList.add("active");
      document.getElementById(tab.dataset.target).classList.add("active");
      setText("authMessage", "");
    });
  });

  // Toggle Admin / User login
  if (toggleAdminBtn) {
    toggleAdminBtn.addEventListener("click", () => {
      if (loginType.value === "user") {
        loginType.value = "admin";
        loginTitle.textContent = "Admin Login";
        toggleAdminBtn.textContent = "Log in as User";
      } else {
        loginType.value = "user";
        loginTitle.textContent = "User Login";
        toggleAdminBtn.textContent = "Log in as Admin";
      }
    });
  }

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      setText("authMessage", "");

      const isUser = loginType.value === "user";
      const endpoint = isUser ? "/api/login" : "/api/admin/login";
      const redirect = isUser ? "/dashboard" : "/admin";

      const result = await postJson(endpoint, {
        username: document.getElementById("loginUsername").value.trim(),
        password: document.getElementById("loginPassword").value
      });

      if (!result?.authenticated && result?.error) {
        setText("authMessage", result.error || "Invalid credentials.");
        return;
      }

      if (result?.authenticated || result?.user) {
         window.location.href = redirect;
      } else {
         setText("authMessage", "Invalid credentials.");
      }
    });
  }

  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      setText("authMessage", "");

      const result = await postJson("/api/register", {
        username: document.getElementById("regUsername").value.trim(),
        password: document.getElementById("regPassword").value
      });

      if (result?.error) {
        setText("authMessage", result.error);
        return;
      }

      window.location.href = "/dashboard";
    });
  }
}
