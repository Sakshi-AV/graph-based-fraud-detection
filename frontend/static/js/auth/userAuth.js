import { postJson, requestJson } from "../api.js";
import { setText } from "../utils.js";

export function initLoginPage() {
  document.getElementById("userLoginForm").addEventListener("submit", handleUserLogin);
}

export function initRegisterPage() {
  document.getElementById("registerForm").addEventListener("submit", handleUserRegister);
}

export async function handleUserLogout() {
  await requestJson("/api/logout", { method: "POST" });
  window.location.href = "/login";
}

async function handleUserLogin(event) {
  event.preventDefault();
  setText("userLoginMessage", "");

  const result = await postJson("/api/login", {
    username: document.getElementById("loginUsername").value.trim(),
    password: document.getElementById("loginPassword").value
  });

  if (result?.error) {
    setText("userLoginMessage", result.error);
    return;
  }

  window.location.href = "/user-dashboard";
}

async function handleUserRegister(event) {
  event.preventDefault();
  setText("registerMessage", "");

  const result = await postJson("/api/register", {
    username: document.getElementById("registerUsername").value.trim(),
    password: document.getElementById("registerPassword").value
  });

  if (result?.error) {
    setText("registerMessage", result.error);
    return;
  }

  window.location.href = "/user-dashboard";
}
