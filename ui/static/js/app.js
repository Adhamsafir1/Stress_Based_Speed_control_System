/* ui/static/js/app.js — Real-time dashboard WebSocket client */

const socket = io();

const COLORS = {
  normal:   "#22c55e",
  mild:     "#eab308",
  high:     "#f97316",
  critical: "#ef4444",
};

// ── DOM refs ───────────────────────────────────────────────
const $ = id => document.getElementById(id);
const connStatus = $("conn-status");
const connText   = $("conn-text");
const stressScore = $("stress-score");
const levelBadge  = $("level-badge");
const levelMsg    = $("level-msg");
const hrVal    = $("hr-val");
const gsrVal   = $("gsr-val");
const spo2Val  = $("spo2-val");
const curSpeed = $("cur-speed");
const tgtSpeed = $("tgt-speed");
const speedBar = $("speed-bar");
const alertList = $("alert-list");

// ── Gauge chart ───────────────────────────────────────────
const gaugeCtx = $("gaugeCanvas").getContext("2d");
const gaugeChart = new Chart(gaugeCtx, {
  type: "doughnut",
  data: {
    datasets: [{
      data: [0, 100],
      backgroundColor: ["#6366f1", "#1a1e2a"],
      borderWidth: 0,
      circumference: 180,
      rotation: 270,
    }],
  },
  options: {
    responsive: false,
    cutout: "76%",
    animation: { duration: 400 },
    plugins: { legend: { display: false }, tooltip: { enabled: false } },
  },
});

function updateGauge(score, level) {
  const color = COLORS[level] || COLORS.normal;
  gaugeChart.data.datasets[0].data = [score, 100 - score];
  gaugeChart.data.datasets[0].backgroundColor[0] = color;
  gaugeChart.update();
}

// ── History chart ─────────────────────────────────────────
const histCtx  = $("histChart").getContext("2d");
const histData = Array(60).fill(null);
const histLabels = Array.from({ length: 60 }, (_, i) => i % 10 === 0 ? `${60 - i}s` : "");

const histChart = new Chart(histCtx, {
  type: "line",
  data: {
    labels: histLabels,
    datasets: [{
      label: "Stress Score",
      data: histData.slice(),
      borderColor: "#6366f1",
      backgroundColor: "rgba(99,102,241,.12)",
      borderWidth: 2,
      pointRadius: 0,
      tension: 0.4,
      fill: true,
    }],
  },
  options: {
    responsive: true,
    animation: false,
    scales: {
      x: { display: false },
      y: {
        min: 0, max: 100,
        grid: { color: "#252836" },
        ticks: { color: "#556070", stepSize: 25 },
      },
    },
    plugins: { legend: { display: false } },
  },
});

function pushHistory(score) {
  histData.shift();
  histData.push(score);
  histChart.data.datasets[0].data = histData.slice();
  histChart.update("none");
}

// ── Main update ───────────────────────────────────────────
function onUpdate(data) {
  const stress = data.stress  || {};
  const speed  = data.speed   || {};
  const sensor = data.sensor  || {};
  const alerts = data.alerts  || [];

  const score = stress.stress_score ?? 0;
  const level = stress.stress_level ?? "normal";
  const color = COLORS[level] || COLORS.normal;

  // Gauge & history
  stressScore.textContent = Math.round(score);
  updateGauge(score, level);
  pushHistory(score);

  // Badge
  levelBadge.textContent      = level.charAt(0).toUpperCase() + level.slice(1);
  levelBadge.style.background = color;
  levelBadge.style.boxShadow  = `0 0 16px ${color}55`;
  levelMsg.textContent         = stress.message || "";

  // Sensors
  hrVal.textContent   = sensor.heart_rate != null ? sensor.heart_rate.toFixed(0) : "--";
  gsrVal.textContent  = sensor.gsr        != null ? sensor.gsr.toFixed(2)        : "--";
  spo2Val.textContent = sensor.spo2       != null ? sensor.spo2.toFixed(1)       : "--";

  // Speed
  curSpeed.textContent = speed.current_speed ?? "--";
  tgtSpeed.textContent = speed.target_speed  ?? "--";
  const pct = Math.min(100, ((speed.current_speed ?? 60) / 100) * 100);
  speedBar.style.width      = `${pct}%`;
  speedBar.style.background = `linear-gradient(90deg, ${color}, ${color}bb)`;

  // Alerts
  if (alerts.length > 0) renderAlerts(alerts);
}

function renderAlerts(alerts) {
  alertList.innerHTML = "";
  alerts.forEach(a => {
    const li = document.createElement("li");
    li.className = `alert-item ${a.stress_level}`;
    li.innerHTML = `
      <span class="alert-time">${a.time_str}</span>
      <span class="alert-msg">${a.message}</span>
    `;
    alertList.appendChild(li);
  });
}

// ── Socket events ─────────────────────────────────────────
socket.on("connect", () => {
  connStatus.classList.add("live");
  connText.textContent = "Live";
});

socket.on("disconnect", () => {
  connStatus.classList.remove("live");
  connText.textContent = "Disconnected";
});

socket.on("update", onUpdate);
