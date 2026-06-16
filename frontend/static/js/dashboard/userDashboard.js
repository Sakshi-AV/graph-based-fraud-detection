import { requestJson } from "../api.js";
import { escapeHtml, formatCurrency, formatPercent, formatTime, setText } from "../utils.js";

export async function initUserDashboardPage() {
  await loadUserDashboard();
}

async function loadUserDashboard() {
  const result = await requestJson("/api/user/dashboard");
  if (result?.error) {
    window.location.href = "/login";
    return;
  }

  setText("userDashboardTitle", `Welcome, ${result.user.username}`);
  setText("userAccountText", `Account ID: ${result.user.account_id}`);
  setText("userTotalTransactions", result.metrics.total);
  setText("userFlaggedTransactions", result.metrics.flagged);
  setText("userPersonalRisk", `${result.metrics.personal_risk}%`);
  renderUserTransactionTable(result.transactions);
}

function renderUserTransactionTable(transactions) {
  const table = document.getElementById("userTransactionsTable");
  if (!table) {
    return;
  }

  if (!transactions.length) {
    table.innerHTML = '<tr><td colspan="7">No transactions yet. Submit one from the monitor page.</td></tr>';
    return;
  }

  table.innerHTML = transactions.map((transaction) => {
    const riskClass = transaction.fraud_prediction === 1 ? "risk-high" : "risk-low";
    const predictionText = transaction.fraud_prediction === 1 ? "Fraud" : "Legitimate";
    return `
      <tr>
        <td>${escapeHtml(transaction.id)}</td>
        <td>${formatTime(transaction.timestamp)}</td>
        <td>${escapeHtml(transaction.receiver)}</td>
        <td>${escapeHtml(transaction.type)}</td>
        <td>${formatCurrency(transaction.amount)}</td>
        <td class="${riskClass}">${predictionText}</td>
        <td>${formatPercent(transaction.fraud_probability)}</td>
      </tr>
    `;
  }).join("");
}
