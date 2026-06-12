import { postJson, requestJson } from "../api.js";
import { setText } from "../utils.js";
import { loadAdminTransactions } from "../dashboard/adminDashboard.js";

export async function initAdminAuth() {
  document.getElementById("adminLoginForm").addEventListener("submit", handleAdminLogin);
  document.getElementById("logoutButton").addEventListener("click", handleAdminLogout);

  const status = await requestJson("/api/admin/status");
  if (status?.authenticated) {
    showAdminDashboard();
    await loadAdminTransactions();
  }
}

async function handleAdminLogin(event) {
  event.preventDefault();
  setText("loginMessage", "");

  const result = await postJson("/api/admin/login", {
    username: document.getElementById("adminUsername").value.trim(),
    password: document.getElementById("adminPassword").value
  });

  if (!result?.authenticated) {
    setText("loginMessage", result?.error || "Invalid admin credentials.");
    return;
  }

  showAdminDashboard();
  await loadAdminTransactions();
}

async function handleAdminLogout() {
  await requestJson("/api/admin/logout", { method: "POST" });
  document.getElementById("adminDashboard").classList.add("hidden");
  document.getElementById("adminLoginView").classList.remove("hidden");
  document.getElementById("adminPassword").value = "";
}

function showAdminDashboard() {
  document.getElementById("adminLoginView").classList.add("hidden");
  document.getElementById("adminDashboard").classList.remove("hidden");
}

