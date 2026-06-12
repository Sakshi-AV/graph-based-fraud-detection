import { initAdminAuth } from "./auth/adminAuth.js";
import { initLoginPage, initRegisterPage } from "./auth/userAuth.js";
import { initAdminDashboard } from "./dashboard/adminDashboard.js";
import { initUserDashboardPage } from "./dashboard/userDashboard.js";
import { initMonitorPage } from "./monitor/scanner.js";

document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page;

  if (page === "monitor") {
    initMonitorPage();
  }

  if (page === "admin") {
    initAdminDashboard();
    initAdminAuth();
  }

  if (page === "login") {
    initLoginPage();
  }

  if (page === "register") {
    initRegisterPage();
  }

  if (page === "user-dashboard") {
    initUserDashboardPage();
  }
});

