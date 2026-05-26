const seedTransactions = [
  { sender: "C1231006815", receiver: "M1979787155", amount: 9839.64, type: "PAYMENT", risk: 6, prediction: 0 },
  { sender: "C1666544295", receiver: "M2044282225", amount: 1864.28, type: "PAYMENT", risk: 4, prediction: 0 },
  { sender: "C1305486145", receiver: "C553264065", amount: 181.00, type: "TRANSFER", risk: 9, prediction: 0 },
  { sender: "C840083671", receiver: "C38997010", amount: 181.00, type: "CASH_OUT", risk: 11, prediction: 0 },
  { sender: "C905080434", receiver: "C476402209", amount: 215310.30, type: "TRANSFER", risk: 38, prediction: 0 },
  { sender: "C764826684", receiver: "C1825419935", amount: 311685.89, type: "CASH_OUT", risk: 48, prediction: 0 },
  { sender: "C977993101", receiver: "C1983025922", amount: 10000000.00, type: "TRANSFER", risk: 91, prediction: 1 }
];

const samples = {
  normal: {
    sender: "C1231006815",
    receiver: "M1979787155",
    amount: 9839.64,
    type: "PAYMENT"
  },
  highRisk: {
    sender: "C900000001",
    receiver: "C900000002",
    amount: 725000.00,
    type: "TRANSFER"
  }
};

const state = {
  transactions: [...seedTransactions],
  riskChart: null,
  modelChart: null
};

document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page;

  if (page === "monitor") {
    initMonitorPage();
  }

  if (page === "admin") {
    initAdminPage();
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

function initMonitorPage() {
  document.getElementById("transactionForm").addEventListener("submit", handleTransactionSubmit);
  document.querySelectorAll("[data-sample]").forEach((button) => {
    button.addEventListener("click", () => loadSample(button.dataset.sample));
  });

  state.riskChart = createRiskChart();
  renderMonitor();
  drawNetwork();
}

async function initAdminPage() {
  document.getElementById("adminLoginForm").addEventListener("submit", handleAdminLogin);
  document.getElementById("logoutButton").addEventListener("click", handleAdminLogout);
  document.getElementById("refreshAdminButton").addEventListener("click", loadAdminTransactions);

  createModelChart();

  const status = await requestJson("/api/admin/status");
  if (status?.authenticated) {
    showAdminDashboard();
    await loadAdminTransactions();
  }
}

function initLoginPage() {
  document.getElementById("userLoginForm").addEventListener("submit", handleUserLogin);
}

function initRegisterPage() {
  document.getElementById("registerForm").addEventListener("submit", handleUserRegister);
}

async function initUserDashboardPage() {
  document.getElementById("userLogoutButton").addEventListener("click", handleUserLogout);
  await loadUserDashboard();
}

function loadSample(sampleName) {
  const sample = samples[sampleName];
  if (!sample) {
    return;
  }

  document.getElementById("sender").value = sample.sender;
  document.getElementById("receiver").value = sample.receiver;
  document.getElementById("amount").value = sample.amount;
  document.getElementById("type").value = sample.type;
}

async function handleTransactionSubmit(event) {
  event.preventDefault();

  const transaction = {
    sender: document.getElementById("sender").value.trim(),
    receiver: document.getElementById("receiver").value.trim(),
    amount: Number(document.getElementById("amount").value),
    type: document.getElementById("type").value
  };

  if (!transaction.sender || !transaction.receiver || !Number.isFinite(transaction.amount) || transaction.amount <= 0) {
    updateResult({
      risk: 0,
      label: "Invalid transaction",
      message: "Sender, receiver, and a positive amount are required.",
      level: "danger"
    });
    return;
  }

  setScanLoading(true);

  try {
    const prediction = await requestJson("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(transaction)
    });

    if (prediction.error) {
      throw new Error(prediction.error);
    }

    const risk = Math.round(prediction.risk_score);
    const result = {
      risk,
      label: prediction.fraud_prediction === 1 ? "Fraud predicted" : "Likely legitimate",
      message: `Model probability: ${formatPercent(prediction.fraud_probability)} using threshold ${formatPercent(prediction.threshold)}. Alerts: ${prediction.alerts?.length || 0}.`,
      level: prediction.fraud_prediction === 1 ? "danger" : risk >= 40 ? "warn" : "safe"
    };

    state.transactions.unshift({
      ...transaction,
      risk,
      prediction: prediction.fraud_prediction,
      probability: prediction.fraud_probability
    });

    updateResult(result);
    renderMonitor();
    drawNetwork();
  } catch (error) {
    updateResult({
      risk: 0,
      label: "Backend unavailable",
      message: `${error.message}. Start the backend with python app.py and open http://127.0.0.1:5000.`,
      level: "danger"
    });
  } finally {
    setScanLoading(false);
  }
}

function setScanLoading(isLoading) {
  const button = document.querySelector(".primary-action");
  if (!button) {
    return;
  }

  button.disabled = isLoading;
  button.textContent = isLoading ? "Running model..." : "Assess risk";
}

async function handleAdminLogin(event) {
  event.preventDefault();
  setText("loginMessage", "");

  const credentials = {
    username: document.getElementById("adminUsername").value.trim(),
    password: document.getElementById("adminPassword").value
  };

  const result = await requestJson("/api/admin/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials)
  });

  if (!result?.authenticated) {
    setText("loginMessage", result?.error || "Invalid admin credentials.");
    return;
  }

  showAdminDashboard();
  await loadAdminTransactions();
}

async function handleUserLogin(event) {
  event.preventDefault();
  setText("userLoginMessage", "");

  const result = await requestJson("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: document.getElementById("loginUsername").value.trim(),
      password: document.getElementById("loginPassword").value
    })
  });

  if (result?.error) {
    setText("userLoginMessage", result.error);
    return;
  }

  window.location.href = "user-dashboard";
}

async function handleUserRegister(event) {
  event.preventDefault();
  setText("registerMessage", "");

  const result = await requestJson("/api/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: document.getElementById("registerUsername").value.trim(),
      password: document.getElementById("registerPassword").value
    })
  });

  if (result?.error) {
    setText("registerMessage", result.error);
    return;
  }

  window.location.href = "user-dashboard";
}

async function handleUserLogout() {
  await requestJson("/api/logout", { method: "POST" });
  window.location.href = "login";
}

async function loadUserDashboard() {
  const result = await requestJson("/api/user/dashboard");
  if (result?.error) {
    window.location.href = "login";
    return;
  }

  setText("userDashboardTitle", `Welcome, ${result.user.username}`);
  setText("userAccountText", `Account ID: ${result.user.account_id}`);
  setText("userTotalTransactions", result.metrics.total);
  setText("userFlaggedTransactions", result.metrics.flagged);
  setText("userPersonalRisk", `${result.metrics.personal_risk}%`);
  renderUserTransactionTable(result.transactions);
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

async function loadAdminTransactions() {
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

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok && !data.error) {
    data.error = `Request failed with status ${response.status}`;
  }

  return data;
}

function buildGraph(transactions) {
  const nodes = new Map();
  const edges = [];

  transactions.forEach((transaction) => {
    const sender = getOrCreateNode(nodes, transaction.sender);
    const receiver = getOrCreateNode(nodes, transaction.receiver);

    sender.outDegree += 1;
    receiver.inDegree += 1;
    sender.degree += 1;
    receiver.degree += 1;

    edges.push({
      source: transaction.sender,
      target: transaction.receiver,
      amount: transaction.amount,
      risk: transaction.risk || 0
    });
  });

  applyPageRank(nodes, edges);
  return { nodes, edges };
}

function emptyNodeStats() {
  return {
    inDegree: 0,
    outDegree: 0,
    degree: 0,
    pageRank: 0
  };
}

function getOrCreateNode(nodes, id) {
  if (!nodes.has(id)) {
    nodes.set(id, emptyNodeStats());
  }
  return nodes.get(id);
}

function applyPageRank(nodes, edges) {
  const nodeIds = [...nodes.keys()];
  if (nodeIds.length === 0) {
    return;
  }

  const damping = 0.85;
  let ranks = Object.fromEntries(nodeIds.map((id) => [id, 1 / nodeIds.length]));

  for (let iteration = 0; iteration < 12; iteration += 1) {
    const nextRanks = Object.fromEntries(nodeIds.map((id) => [id, (1 - damping) / nodeIds.length]));

    nodeIds.forEach((id) => {
      const outgoing = edges.filter((edge) => edge.source === id);
      if (outgoing.length === 0) {
        return;
      }

      outgoing.forEach((edge) => {
        nextRanks[edge.target] += damping * (ranks[id] / outgoing.length);
      });
    });

    ranks = nextRanks;
  }

  nodeIds.forEach((id) => {
    nodes.get(id).pageRank = ranks[id];
  });
}

function renderMonitor() {
  const graph = buildGraph(state.transactions);
  const risks = state.transactions.map((transaction) => transaction.risk || 0);
  const flagged = state.transactions.filter((transaction) => transaction.prediction === 1).length;
  const averageRisk = risks.length
    ? Math.round(risks.reduce((total, risk) => total + risk, 0) / risks.length)
    : 0;

  setText("totalTransactions", state.transactions.length);
  setText("flaggedTransactions", flagged);
  setText("averageRisk", `${averageRisk}%`);
  setText("knownAccounts", graph.nodes.size);
  setText("graphSummary", `${graph.nodes.size} nodes, ${graph.edges.length} edges`);

  renderTransactionTable();
  updateRiskChart();
}

function renderTransactionTable() {
  const table = document.getElementById("transactionTable");
  if (!table) {
    return;
  }

  table.innerHTML = state.transactions.slice(0, 8).map((transaction) => {
    const riskClass = transaction.prediction === 1 ? "risk-high" : transaction.risk >= 40 ? "risk-mid" : "risk-low";
    return `
      <tr>
        <td>${escapeHtml(transaction.sender)}</td>
        <td>${escapeHtml(transaction.receiver)}</td>
        <td>${escapeHtml(transaction.type)}</td>
        <td>${formatCurrency(transaction.amount)}</td>
        <td class="${riskClass}">${transaction.risk}%</td>
      </tr>
    `;
  }).join("");
}

function createRiskChart() {
  const chartTarget = document.getElementById("riskChart");
  if (!chartTarget || !window.Chart) {
    return null;
  }

  return new Chart(chartTarget, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        label: "Model probability",
        data: [],
        borderColor: "#5eb1ff",
        backgroundColor: "rgba(94, 177, 255, 0.15)",
        tension: 0.32,
        fill: true,
        pointRadius: 4
      }]
    },
    options: getChartOptions(100)
  });
}

function createModelChart() {
  const chartTarget = document.getElementById("modelChart");
  if (!chartTarget || !window.Chart) {
    return;
  }

  state.modelChart = new Chart(chartTarget, {
    type: "bar",
    data: {
      labels: ["Precision", "Recall", "F1-score"],
      datasets: [{
        label: "Fraud class performance",
        data: [1.0, 0.4348, 0.6061],
        backgroundColor: ["#44d19d", "#f5c451", "#5eb1ff"],
        borderRadius: 6
      }]
    },
    options: getChartOptions(1)
  });
}

function getChartOptions(maxValue) {
  return {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true,
        max: maxValue,
        ticks: { color: "#9caab8" },
        grid: { color: "rgba(255,255,255,0.08)" }
      },
      x: {
        ticks: { color: "#9caab8" },
        grid: { display: false }
      }
    },
    plugins: {
      legend: {
        labels: { color: "#edf2f6" }
      }
    }
  };
}

function updateRiskChart() {
  if (!state.riskChart) {
    return;
  }

  const recent = [...state.transactions].slice(0, 8).reverse();
  state.riskChart.data.labels = recent.map((_, index) => `T${index + 1}`);
  state.riskChart.data.datasets[0].data = recent.map((transaction) => transaction.risk || 0);
  state.riskChart.update();
}

function updateResult(result) {
  const card = document.getElementById("resultCard");
  if (!card) {
    return;
  }

  card.className = `result-card ${result.level}`;
  setText("resultTitle", `${result.label}: ${result.risk}%`);
  setText("resultText", result.message);
  document.getElementById("riskFill").style.width = `${result.risk}%`;
}

function drawNetwork() {
  const canvas = document.getElementById("networkCanvas");
  if (!canvas) {
    return;
  }

  const ctx = canvas.getContext("2d");
  const graph = buildGraph(state.transactions);
  const nodes = [...graph.nodes.keys()];
  const width = canvas.width;
  const height = canvas.height;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) * 0.36;

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#0e141a";
  ctx.fillRect(0, 0, width, height);

  const positions = new Map();
  nodes.forEach((id, index) => {
    const angle = (Math.PI * 2 * index) / nodes.length - Math.PI / 2;
    positions.set(id, {
      x: centerX + Math.cos(angle) * radius,
      y: centerY + Math.sin(angle) * radius
    });
  });

  graph.edges.slice(-24).forEach((edge) => {
    const source = positions.get(edge.source);
    const target = positions.get(edge.target);
    if (!source || !target) {
      return;
    }

    ctx.strokeStyle = edge.risk >= 70 ? "rgba(255,107,107,0.82)" : "rgba(94,177,255,0.38)";
    ctx.lineWidth = Math.max(1, Math.min(5, Math.log10(edge.amount + 1)));
    ctx.beginPath();
    ctx.moveTo(source.x, source.y);
    ctx.lineTo(target.x, target.y);
    ctx.stroke();
  });

  nodes.forEach((id) => {
    const node = graph.nodes.get(id);
    const position = positions.get(id);
    const nodeRadius = 7 + Math.min(10, node.degree * 1.4);

    ctx.beginPath();
    ctx.fillStyle = node.pageRank > 0.16 ? "#f5c451" : "#44d19d";
    ctx.arc(position.x, position.y, nodeRadius, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#dbe5ed";
    ctx.font = "12px Segoe UI";
    ctx.textAlign = "center";
    ctx.fillText(shortId(id), position.x, position.y + nodeRadius + 16);
  });
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = value;
  }
}

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0
  }).format(value);
}

function formatPercent(value) {
  return `${(Number(value) * 100).toFixed(2)}%`;
}

function formatTime(value) {
  return new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  }).format(new Date(value));
}

function shortId(id) {
  return id.length > 8 ? `${id.slice(0, 4)}...${id.slice(-3)}` : id;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
