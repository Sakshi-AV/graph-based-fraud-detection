export function createRiskChart() {
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

export function createModelChart() {
  const chartTarget = document.getElementById("modelChart");
  if (!chartTarget || !window.Chart) {
    return null;
  }

  return new Chart(chartTarget, {
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

export function updateRiskChart(chart, transactions) {
  if (!chart) {
    return;
  }

  const recent = [...transactions].slice(0, 8).reverse();
  chart.data.labels = recent.map((_, index) => `T${index + 1}`);
  chart.data.datasets[0].data = recent.map((transaction) => transaction.risk || 0);
  chart.update();
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

