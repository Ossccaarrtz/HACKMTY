// =========================================================
// FECHA EN EL HEADER
// =========================================================
function updateDate() {
  const now = new Date();
  const options = {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  };
  const dateElement = document.getElementById("currentDate");
  if (dateElement)
    dateElement.textContent = now
      .toLocaleDateString("es-MX", options)
      .toUpperCase();
}
updateDate();

// =========================================================
// CARRUSEL HERO
// =========================================================
let currentSlide = 0;
const slides = document.querySelectorAll(".carousel-slide");
const indicators = document.querySelectorAll(".indicator");
const carouselTrack = document.getElementById("carouselTrack");

function showSlide(index) {
  currentSlide = index;
  if (carouselTrack)
    carouselTrack.style.transform = `translateX(-${currentSlide * 100}%)`;
  indicators.forEach((indicator, i) =>
    indicator.classList.toggle("active", i === currentSlide)
  );
}
indicators.forEach((indicator, i) =>
  indicator.addEventListener("click", () => showSlide(i))
);
setInterval(() => {
  currentSlide = (currentSlide + 1) % slides.length;
  showSlide(currentSlide);
}, 5000);

// =========================================================
// ANIMAR KPIs
// =========================================================
function animateValue(id, start, end, duration, prefix = "$", suffix = "") {
  const obj = document.getElementById(id);
  if (!obj) return;
  const range = end - start;
  const increment = end > start ? 1 : -1;
  const stepTime = Math.abs(Math.floor(duration / range));
  let current = start;
  const timer = setInterval(() => {
    current += increment * Math.ceil(range / 100);
    if (
      (increment > 0 && current >= end) ||
      (increment < 0 && current <= end)
    ) {
      current = end;
      clearInterval(timer);
    }
    obj.textContent = prefix + current.toLocaleString("es-MX") + suffix;
  }, stepTime);
}
setTimeout(() => {
  animateValue("ingresos", 0, 2450000, 1500);
  animateValue("gastos", 0, 1850000, 1500);
  animateValue("flujo", 0, 600000, 1500);
  animateValue("margen", 0, 24.5, 1500, "", "%");
}, 300);

// =========================================================
// CHARTS DINÁMICOS (INCLUYE PROPHET)
// =========================================================
const chartColors = {
  primary: "#e30613",
  secondary: "#1e3a8a",
  success: "#059669",
  warning: "#f59e0b",
  info: "#3b82f6",
};

// 🔮 Cargar forecast desde backend
async function fetchForecast(serie) {
  try {
    const res = await fetch(`http://127.0.0.1:8000/forecast/${serie}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.slice(-10); // últimos 10 puntos
  } catch (err) {
    console.error("❌ Error al obtener forecast:", err);
    return null;
  }
}

function createChart(ctxId, config) {
  const ctx = document.getElementById(ctxId);
  if (!ctx) return;
  new Chart(ctx.getContext("2d"), config);
}

// --- USD/MXN (Datos reales de Prophet) ---
(async () => {
  const forecast = await fetchForecast("tipo_cambio_fix");
  const ctx = document.getElementById("usdChart");
  if (!ctx) return;

  const labels = forecast
    ? forecast.map((p) => new Date(p.ds).toLocaleDateString("es-MX"))
    : [];
  const predData = forecast ? forecast.map((p) => p.yhat.toFixed(2)) : [];

  new Chart(ctx.getContext("2d"), {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Predicción (Prophet)",
          data: predData,
          borderColor: chartColors.primary,
          backgroundColor: "rgba(227, 6, 19, 0.1)",
          borderDash: [5, 5],
          tension: 0.4,
          fill: true,
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: "top",
          labels: { usePointStyle: true, padding: 15 },
        },
      },
      scales: {
        y: {
          beginAtZero: false,
          grid: { color: "rgba(0,0,0,0.05)" },
          ticks: { callback: (v) => v + " MXN" },
        },
        x: { grid: { display: false } },
      },
    },
  });
})();

// --- INFLACIÓN (placeholder) ---
createChart("inflacionChart", {
  type: "line",
  data: {
    labels: [
      "Ene",
      "Feb",
      "Mar",
      "Abr",
      "May",
      "Jun",
      "Jul",
      "Ago",
      "Sep",
      "Oct",
    ],
    datasets: [
      {
        label: "Histórico",
        data: [4.8, 4.9, 5.1, 5.3, 5.2, 5.4, 5.6, 5.5, 5.7, 5.8],
        borderColor: chartColors.warning,
        backgroundColor: "rgba(245,158,11,0.1)",
        tension: 0.4,
        fill: true,
        borderWidth: 2,
      },
      {
        label: "Predicción (Dummy)",
        data: [null, null, null, null, null, null, null, 5.5, 5.7, 5.9],
        borderColor: chartColors.primary,
        backgroundColor: "rgba(227,6,19,0.1)",
        borderDash: [5, 5],
        tension: 0.4,
        fill: true,
        borderWidth: 2,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: true, position: "top" } },
    scales: {
      y: {
        beginAtZero: false,
        min: 4,
        max: 7,
        ticks: { callback: (v) => v + "%" },
      },
      x: { grid: { display: false } },
    },
  },
});

// --- INGRESOS ---
createChart("ingresosChart", {
  type: "bar",
  data: {
    labels: [
      "Ene",
      "Feb",
      "Mar",
      "Abr",
      "May",
      "Jun",
      "Jul",
      "Ago",
      "Sep",
      "Oct",
    ],
    datasets: [
      {
        label: "Ingresos (MXN)",
        data: [
          2100000, 2250000, 2180000, 2350000, 2420000, 2380000, 2450000,
          2500000, 2480000, 2550000,
        ],
        backgroundColor: chartColors.success,
        borderRadius: 8,
        borderWidth: 0,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { callback: (v) => "$" + (v / 1000000).toFixed(1) + "M" },
      },
      x: { grid: { display: false } },
    },
  },
});

// =========================================================
// SIMULADOR WHAT-IF
// =========================================================
const sliders = ["precios", "gastos", "tipoCambio"];
sliders.forEach((id) => {
  const slider = document.getElementById(id + "Slider");
  const value = document.getElementById(id + "Value");
  if (slider && value) {
    slider.addEventListener(
      "input",
      (e) => (value.textContent = e.target.value + "%")
    );
  }
});
const simularBtn = document.getElementById("simularBtn");
if (simularBtn) {
  simularBtn.addEventListener("click", () => {
    const ingresosBase = 2450000,
      gastosBase = 1850000,
      flujoBase = 600000;
    const preciosChange = parseFloat(
      document.getElementById("preciosSlider").value
    );
    const gastosChange = parseFloat(
      document.getElementById("gastosSlider").value
    );
    const tipoCambioChange = parseFloat(
      document.getElementById("tipoCambioSlider").value
    );
    const nuevosIngresos = ingresosBase * (1 + preciosChange / 100);
    const nuevosGastos =
      gastosBase * (1 - gastosChange / 100) * (1 + tipoCambioChange / 100);
    const nuevoFlujo = nuevosIngresos - nuevosGastos;
    const cambioFlujo = (((nuevoFlujo - flujoBase) / flujoBase) * 100).toFixed(
      1
    );
    const simulatorResults = document.getElementById("simulatorResults");
    simulatorResults.innerHTML = `
      <p class="result-text"><strong>Resultados de la Simulación:</strong></p>
      <p class="result-text">• Ingresos Proyectados: $${nuevosIngresos.toLocaleString(
        "es-MX"
      )}</p>
      <p class="result-text">• Gastos Proyectados: $${nuevosGastos.toLocaleString(
        "es-MX"
      )}</p>
      <p class="result-text">• Flujo de Caja Proyectado: $${nuevoFlujo.toLocaleString(
        "es-MX"
      )}</p>
      <p class="result-text" style="color:${
        cambioFlujo >= 0 ? "#059669" : "#dc2626"
      };font-weight:700;">
        ${cambioFlujo >= 0 ? "↑" : "↓"} Variación en flujo: ${Math.abs(
      cambioFlujo
    )}%
      </p>`;
  });
}

// =========================================================
// CHAT FLOTANTE + VOZ IA
// =========================================================
(() => {
  const qs = (sel) => document.querySelector(sel);

  const chatToggle = qs("#chatToggle");
  const chatBackdrop = qs("#chatBackdrop");
  const chatWindow = qs("#chatWindow");
  const chatBody = qs("#chatBody");
  const chatInput = qs("#chatInput");
  const chatSendBtn = qs("#chatSendBtn");
  const chatCloseBtn = qs("#chatCloseBtn");

  const voiceModeBtn = qs("#voiceModeBtn");
  const voiceOverlay = qs("#voiceOverlay");
  const voiceStopBtn = qs("#voiceStopBtn");
  const voiceCanvas = qs("#voiceWaves");
  const dragHandle = qs("#chatDragHandle");

  // ---- Abrir / cerrar chat ----
  function openChat() {
    chatBackdrop.classList.remove("hidden");
    chatToggle.style.display = "none";
  }
  function closeChat() {
    chatBackdrop.classList.add("hidden");
    chatToggle.style.display = "";
  }

  chatToggle?.addEventListener("click", openChat);
  chatCloseBtn?.addEventListener("click", closeChat);
  chatBackdrop?.addEventListener("click", (e) => {
    if (e.target === chatBackdrop) closeChat();
  });

  // ---- Enviar mensaje ----
  function appendMessage(text, who = "user") {
    const div = document.createElement("div");
    div.className = `msg ${who}`;
    div.textContent = text;
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  async function sendChat() {
    const text = (chatInput?.value || "").trim();
    if (!text) return;
    appendMessage(text, "user");
    chatInput.value = "";

    appendMessage("🤖 Analizando tu consulta...", "bot");

    try {
      const res = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text }),
      });
      const data = await res.json();
      appendMessage(data.text || "No se obtuvo respuesta.", "bot");
    } catch (err) {
      appendMessage("Error al conectar con el servidor.", "bot");
      console.error(err);
    }
  }

  chatSendBtn?.addEventListener("click", sendChat);
  chatInput?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendChat();
  });

  // ---- Arrastrar ventana ----
  let isDragging = false,
    startX = 0,
    startY = 0,
    startLeft = 0,
    startTop = 0;
  const canDrag = () => window.matchMedia("(min-width: 992px)").matches;

  dragHandle?.addEventListener("mousedown", (e) => {
    if (!canDrag()) return;
    isDragging = true;
    const rect = chatWindow.getBoundingClientRect();
    startX = e.clientX;
    startY = e.clientY;
    startLeft = rect.left;
    startTop = rect.top;
    document.body.style.userSelect = "none";
  });
  window.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;
    chatWindow.style.position = "fixed";
    chatWindow.style.left = `${startLeft + dx}px`;
    chatWindow.style.top = `${startTop + dy}px`;
  });
  window.addEventListener("mouseup", () => {
    if (isDragging) {
      isDragging = false;
      document.body.style.userSelect = "";
    }
  });

  // ---- Modo voz ----
  let audioCtx, analyser, micStream, dataArray, rafId;

  async function startVoice() {
    try {
      micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const src = audioCtx.createMediaStreamSource(micStream);
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      const bufferLength = analyser.frequencyBinCount;
      dataArray = new Uint8Array(bufferLength);
      src.connect(analyser);
      voiceOverlay.classList.remove("hidden");
      drawWaves();
    } catch (err) {
      alert("No se pudo acceder al micrófono. Verifica permisos.");
      console.error(err);
    }
  }

  function stopVoice() {
    cancelAnimationFrame(rafId);
    if (micStream) micStream.getTracks().forEach((t) => t.stop());
    if (audioCtx) audioCtx.close();
    micStream = null;
    audioCtx = null;
    analyser = null;
    voiceOverlay.classList.add("hidden");
  }

  function drawWaves() {
    const ctx = voiceCanvas.getContext("2d");
    const W = voiceCanvas.width,
      H = voiceCanvas.height;
    function loop() {
      rafId = requestAnimationFrame(loop);
      if (!analyser) return;
      analyser.getByteFrequencyData(dataArray);
      ctx.clearRect(0, 0, W, H);
      const bars = 40;
      const step = Math.floor(dataArray.length / bars);
      for (let i = 0; i < bars; i++) {
        const v = dataArray[i * step] / 255;
        const h = v * (H - 6);
        const x = (W / bars) * i + 2;
        const y = H - h;
        ctx.fillStyle = "#ec1c2e";
        ctx.fillRect(x, y, W / bars - 6, h);
      }
    }
    loop();
  }

  voiceModeBtn?.addEventListener("click", startVoice);
  voiceStopBtn?.addEventListener("click", stopVoice);
  voiceOverlay?.addEventListener("click", (e) => {
    if (e.target === voiceOverlay) stopVoice();
  });
})();
