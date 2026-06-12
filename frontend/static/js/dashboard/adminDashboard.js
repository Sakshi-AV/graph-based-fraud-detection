import { requestJson } from "../api.js";
import { createModelChart } from "../charts.js";
import { escapeHtml, formatCurrency, formatPercent, formatTime, setText } from "../utils.js";

export function initAdminDashboard() {
  document.getElementById("refreshAdminButton").addEventListener("click", loadAdminTransactions);
  createModelChart();
}

export async function loadAdminTransactions() {
  const result = await requestJson("/api/admin/transactions");
  if (result?.error) {
    return;
  }

  setText("adminTotal", result.metrics.total);
  setText("adminFlagged", result.metrics.flagged);
  setText("adminAverageRisk", `${result.metrics.average_risk}%`);
  setText("adminTotalUsers", result.metrics.total_users);
  setText("adminActiveUsers", result.metrics.active_users);
  setText("adminFlaggedUsers", result.metrics.flagged_users);
  setText("adminFraudPercentage", `${result.metrics.fraud_percentage}%`);
  renderAdminTransactionTable(result.transactions);
  renderAdminAlerts(result.alerts || []);
  renderTopRiskyAccounts(result.top_risky_accounts || []);
}

function renderAdminTransactionTable(transactions) {
  const table = document.getElementById("adminTransactionsTable");
  if (!table) {
    return;
  }

  if (!transactions.length) {
    table.innerHTML = '<tr><td colspan="8">No transactions submitted yet.</td></tr>';
    return;
  }

  table.innerHTML = transactions.map((transaction) => {
    const riskClass = transaction.fraud_prediction === 1 ? "risk-high" : "risk-low";
    const predictionText = transaction.fraud_prediction === 1 ? "Fraud" : "Legitimate";

    return `
      <tr>
        <td>${escapeHtml(transaction.id)}</td>
        <td>${formatTime(transaction.timestamp)}</td>
        <td>${escapeHtml(transaction.sender)}</td>
        <td>${escapeHtml(transaction.receiver)}</td>
        <td>${escapeHtml(transaction.type)}</td>
        <td>${formatCurrency(transaction.amount)}</td>
        <td class="${riskClass}">${predictionText}</td>
        <td>${formatPercent(transaction.fraud_probability)}</td>
      </tr>
    `;
  }).join("");
}

function renderAdminAlerts(alerts) {
  const list = document.getElementById("adminAlertsList");
  if (!list) {
    return;
  }

  if (!alerts.length) {
    list.innerHTML = "<li>No alerts yet.</li>";
    return;
  }

  list.innerHTML = alerts.slice(0, 8).map((alert) => `
    <li>
      <strong>${escapeHtml(alert.alert_type)}</strong>
      <span>${escapeHtml(alert.message)}</span>
    </li>
  `).join("");
}

function renderTopRiskyAccounts(accounts) {
  const list = document.getElementById("topRiskyAccounts");
  if (!list) {
    return;
  }

  if (!accounts.length) {
    list.innerHTML = "<li>No risky accounts yet.</li>";
    return;
  }

  list.innerHTML = accounts.map((account) => `
    <li>
      <strong>${escapeHtml(account.account_id)}</strong>
      <span>${formatPercent(account.average_probability)} average risk across ${account.total} transaction(s)</span>
    </li>
  `).join("");
}

