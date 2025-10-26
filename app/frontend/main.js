// =========================================================
// CONFIGURACIÓN DEL BACKEND
// =========================================================
const BACKEND_URL = "http://localhost:8000";

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

  const dateMobile = document.getElementById("currentDateMobile");
  if (dateMobile)
    dateMobile.textContent = now
      .toLocaleDateString("es-MX", options)
      .toUpperCase();
}
updateDate();

// =========================================================
// MENÚ MÓVIL
// =========================================================
const hamburgerBtn = document.getElementById("hamburgerBtn");
const closeMenuBtn = document.getElementById("closeMenuBtn");
const mobileMenu = document.getElementById("mobileMenu");
const menuOverlay = document.getElementById("menuOverlay");

if (hamburgerBtn && mobileMenu) {
  hamburgerBtn.addEventListener("click", () => {
    mobileMenu.classList.add("open");
    menuOverlay.hidden = false;
    hamburgerBtn.classList.add("is-active");
  });
}

if (closeMenuBtn && mobileMenu) {
  closeMenuBtn.addEventListener("click", () => {
    mobileMenu.classList.remove("open");
    menuOverlay.hidden = true;
    hamburgerBtn.classList.remove("is-active");
  });
}

if (menuOverlay) {
  menuOverlay.addEventListener("click", () => {
    mobileMenu.classList.remove("open");
    menuOverlay.hidden = true;
    hamburgerBtn.classList.remove("is-active");
  });
}

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
// CHARTS
// =========================================================
const chartColors = {
  primary: "#e30613",
  secondary: "#1e3a8a",
  success: "#059669",
  warning: "#f59e0b",
  info: "#3b82f6",
};

function createChart(ctxId, config) {
  const ctx = document.getElementById(ctxId);
  if (!ctx) return;
  new Chart(ctx.getContext("2d"), config);
}

// --- USD/MXN ---
createChart("usdChart", {
  type: "line",
  data: {
    labels: [
      "Día 1",
      "Día 2",
      "Día 3",
      "Día 4",
      "Día 5",
      "Día 6",
      "Día 7",
      "Día 8",
      "Día 9",
      "Día 10",
    ],
    datasets: [
      {
        label: "Histórico",
        data: [
          20.15, 20.18, 20.12, 20.25, 20.3, 20.28, 20.35, 20.4, 20.38, 20.42,
        ],
        borderColor: chartColors.secondary,
        backgroundColor: "rgba(30, 58, 138, 0.1)",
        tension: 0.4,
        fill: true,
        borderWidth: 2,
      },
      {
        label: "Predicción",
        data: [null, null, null, null, null, null, null, 20.4, 20.45, 20.48],
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
        min: 20,
        max: 21,
        grid: { color: "rgba(0,0,0,0.05)" },
      },
      x: { grid: { display: false } },
    },
  },
});

// --- INFLACIÓN ---
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
        label: "Predicción",
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

// ALERTAS INTELIGENTES - INTERACCIÓN DE BOTONES
// =========================================================

// Detectar todos los botones de alertas
document.addEventListener("DOMContentLoaded", () => {
  const alertCards = document.querySelectorAll(".alert-card");

  alertCards.forEach((card) => {
    card.addEventListener("click", (e) => {
      const target = e.target;

      // --- 1. BOTONES QUE ELIMINAN LA ALERTA ---
      if (
        target.textContent.includes("ACEPTAR") ||
        target.textContent.includes("POSPONER")
      ) {
        card.classList.add("fade-out");
        setTimeout(() => card.remove(), 500); // elimina tras animación
      }

      // --- 2. BOTONES QUE ABREN MODAL ---
      if (
        target.textContent.includes("REVISAR") ||
        target.textContent.includes("VER DETALLES")
      ) {
        const title = card.querySelector("h4").textContent;
        const details = card.querySelector("p").textContent;

        const modal = document.createElement("div");
        modal.className = "alert-modal";
        modal.innerHTML = `
          <div class="alert-modal-content">
            <h3>${title}</h3>
            <p>${details}</p>
            <p style="margin-top:1rem;">📊 <strong>Análisis detallado:</strong> Esta alerta se generó a partir del modelo Prophet (META) con datos históricos y tendencias de los últimos 30 días. Puede consultar las proyecciones en la sección “Análisis Predictivo”.</p>
            <div class="alert-modal-actions">
              <button class="btn btn-primary" id="closeAlertModal">Cerrar</button>
            </div>
          </div>
        `;
        document.body.appendChild(modal);

        // Cerrar modal
        modal
          .querySelector("#closeAlertModal")
          .addEventListener("click", () => {
            modal.classList.add("fade-out");
            setTimeout(() => modal.remove(), 300);
          });
      }
    });
  });
});

// =========================================================
// RESUMEN EJECUTIVO CON RECOMENDACIONES BANORTE
// =========================================================
function generarResumenEjecutivo() {
  const ingresos = 2450000;
  const gastos = 1850000;
  const flujo = 600000;
  const margen = 24.5;

  const estado =
    flujo > 500000 && margen > 20
      ? "Bueno"
      : flujo > 300000
      ? "Regular"
      : "En riesgo";

  let recomendacion = "";
  if (estado === "Bueno") {
    recomendacion =
      "La empresa presenta buena salud financiera. Banorte recomienda explorar opciones de inversión en instrumentos de bajo riesgo o expansión controlada.";
  } else if (estado === "Regular") {
    recomendacion =
      "La empresa mantiene estabilidad, pero debe reforzar su flujo de caja. Banorte recomienda revisar líneas de crédito y optimizar gastos operativos.";
  } else {
    recomendacion =
      "La empresa está en zona de riesgo financiero. Se sugiere revisar estructura de deuda y considerar financiamiento Banorte para estabilizar liquidez.";
  }

  const resumenContainer = document.getElementById("resumenEjecutivo");
  if (resumenContainer) {
    resumenContainer.innerHTML = `
      <div class="executive-summary fade-in">
        <h3>Resumen Ejecutivo</h3>
        <p><strong>Estado financiero:</strong> ${estado}</p>
        <p>${recomendacion}</p>
      </div>`;
  }
}

// Ejecutar después de cargar
document.addEventListener("DOMContentLoaded", generarResumenEjecutivo);

// =========================================================
// DESGLOSE INTERACTIVO DE KPI (EMPRESA DE DIVISAS)
// =========================================================
const kpiDetalles = {
  ingresos: {
    titulo: "Ingresos",
    texto: `
      <strong>Fuente principal:</strong> Conversión USD/MXN y transferencias internacionales.<br><br>
      Los ingresos aumentaron un 4.2% debido a la apreciación del peso y a un mayor volumen de operaciones minoristas.
      <br><br>
      <strong>Recomendación:</strong> Mantener tarifas competitivas en operaciones de cambio y explorar alianzas con corredores institucionales.
    `,
  },
  gastos: {
    titulo: "Gastos",
    texto: `
      <strong>Principales rubros:</strong> comisiones bancarias, mantenimiento de sistemas y cobertura de riesgo cambiario.<br><br>
      Los gastos se redujeron 2.1% gracias a una renegociación de tarifas con corresponsales internacionales.
      <br><br>
      <strong>Recomendación:</strong> Optimizar costos tecnológicos mediante automatización de conciliaciones y control de spreads.
    `,
  },
  flujo: {
    titulo: "Flujo de Caja",
    texto: `
      <strong>Contexto:</strong> El flujo positivo de $600,000 refleja una sólida gestión de liquidez pese a la volatilidad cambiaria.
      <br><br>
      <strong>Riesgos:</strong> una depreciación del peso o bajas en el volumen de remesas podrían reducir la liquidez disponible.
      <br><br>
      <strong>Recomendación:</strong> Mantener reservas en dólares y explorar instrumentos de cobertura Banorte FX Shield.
    `,
  },
  margen: {
    titulo: "Margen Neto",
    texto: `
      <strong>Desempeño:</strong> Margen del 24.5%, impulsado por el diferencial favorable entre compra y venta de divisas.
      <br><br>
      <strong>Interpretación:</strong> La empresa opera con rentabilidad saludable, aunque sensible a la volatilidad del mercado.
      <br><br>
      <strong>Recomendación:</strong> Considerar inversión en infraestructura digital Banorte para aumentar la eficiencia operativa.
    `,
  },
};

// Detectar clics sobre las tarjetas KPI
document.querySelectorAll(".kpi-card").forEach((card) => {
  card.addEventListener("click", () => {
    const id = card.getAttribute("data-id");
    if (!id || !kpiDetalles[id]) return;

    const info = kpiDetalles[id];
    const modal = document.createElement("div");
    modal.className = "chart-modal";
    modal.innerHTML = `
      <div class="chart-modal-content">
        <h3>${info.titulo}</h3>
        <p>${info.texto}</p>
        <button id="closeModalBtn">Cerrar</button>
      </div>`;
    document.body.appendChild(modal);
    document
      .getElementById("closeModalBtn")
      .addEventListener("click", () => modal.remove());
  });
});

// =========================================================
// KPI SECUNDARIOS - DETALLES INTERACTIVOS
// =========================================================
const kpiInfo = {
  roe: {
    titulo: "ROE (Return on Equity)",
    descripcion: `
      <strong>Qué mide:</strong> rentabilidad sobre el capital invertido por los socios.<br><br>
      <strong>Resultado:</strong> 18.2% indica que la empresa genera $0.18 por cada peso de capital.<br><br>
      <strong>Recomendación Banorte:</strong> destina parte de tus utilidades a fondos de inversión empresariales
      para mejorar el rendimiento del capital propio.`,
  },
  liquidez: {
    titulo: "Liquidez Corriente",
    descripcion: `
      <strong>Qué mide:</strong> capacidad de pagar deudas de corto plazo.<br><br>
      <strong>Resultado:</strong> Razón 1.8 — solvencia estable y bajo riesgo de liquidez.<br><br>
      <strong>Recomendación:</strong> mantén reservas en efectivo para cubrir 3 meses de operaciones.`,
  },
  endeudamiento: {
    titulo: "Endeudamiento Total",
    descripcion: `
      <strong>Qué mide:</strong> porcentaje de activos financiados con deuda.<br><br>
      <strong>Resultado:</strong> 42% — nivel saludable. La empresa aprovecha apalancamiento sin sobreendeudarse.<br><br>
      <strong>Recomendación Banorte:</strong> si buscas expansión, podrías acceder a un crédito PyME preferencial.`,
  },
  crecimiento: {
    titulo: "Crecimiento de Ingresos",
    descripcion: `
      <strong>Qué mide:</strong> evolución de los ingresos frente al mes anterior.<br><br>
      <strong>Resultado:</strong> +4.2% — tendencia positiva por aumento en operaciones USD/MXN.<br><br>
      <strong>Recomendación:</strong> consolida esta tendencia con estrategias de fidelización de clientes.`,
  },
};

// Mostrar modal al hacer clic
document.querySelectorAll(".kpi-mini").forEach((mini) => {
  mini.addEventListener("click", () => {
    const id = mini.dataset.id;
    const info = kpiInfo[id];
    if (!info) return;

    const modal = document.createElement("div");
    modal.className = "kpi-modal";
    modal.innerHTML = `
      <div class="kpi-modal-content">
        <h3>${info.titulo}</h3>
        <p>${info.descripcion}</p>
        <button id="closeKpiModal">Cerrar</button>
      </div>
    `;
    document.body.appendChild(modal);

    document.getElementById("closeKpiModal").addEventListener("click", () => {
      modal.remove();
    });
  });
});

// =========================================================
// DESCRIPCIONES AL HACER CLICK EN LAS GRÁFICAS
// =========================================================
const chartDescriptions = {
  usdChart: {
    title: "Cambio USD/MXN",
    text: "Muestra la evolución y predicción del tipo de cambio. Es crucial para empresas que importan o exportan, ya que un dólar más caro puede reducir el margen o aumentar costos.",
  },
  inflacionChart: {
    title: "Inflación",
    text: "Refleja la tendencia de los precios generales. Una inflación alta erosiona el poder de compra y afecta la planeación financiera de la empresa.",
  },
  ingresosChart: {
    title: "Ingresos proyectados",
    text: "Permite observar la tendencia de crecimiento mensual. Un aumento sostenido indica estabilidad y oportunidad de inversión.",
  },
};

Object.keys(chartDescriptions).forEach((id) => {
  const canvas = document.getElementById(id);
  if (!canvas) return;
  canvas.addEventListener("click", () => {
    const info = chartDescriptions[id];
    const modal = document.createElement("div");
    modal.className = "chart-modal";
    modal.innerHTML = `
      <div class="chart-modal-content">
        <h3>${info.title}</h3>
        <p>${info.text}</p>
        <button id="closeModalBtn">Cerrar</button>
      </div>`;
    document.body.appendChild(modal);
    document
      .getElementById("closeModalBtn")
      .addEventListener("click", () => modal.remove());
  });
});

/// =========================================================
// CARRUSEL HERO (actualizado con imágenes y texto a la izquierda)
// =========================================================
let currentHeroSlide = 0;
const heroSlides = document.querySelectorAll(".hero-slide");

function changeHeroSlide() {
  heroSlides[currentHeroSlide].classList.remove("active");
  currentHeroSlide = (currentHeroSlide + 1) % heroSlides.length;
  heroSlides[currentHeroSlide].classList.add("active");
}

// Cambia cada 5 segundos
if (heroSlides.length > 0) {
  setInterval(changeHeroSlide, 5000);
}

// =========================================================
// ================== CHAT CON IA (TEXTO + VOZ) ============
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
  const inlineMicBtn = qs("#inlineMicBtn");
  const voiceModeBtn = qs("#voiceModeBtn");

  const voiceOverlay = qs("#voiceOverlay");
  const voiceStopBtn = qs("#voiceStopBtn");
  const voiceCanvas = qs("#voiceWaves");
  const dragHandle = qs("#chatDragHandle");

  // ---- Abrir / cerrar chat ----
  function openChat() {
    chatBackdrop?.classList.remove("hidden");
    if (chatToggle) chatToggle.style.display = "none";
  }

  function closeChat() {
    chatBackdrop?.classList.add("hidden");
    if (chatToggle) chatToggle.style.display = "";
  }

  chatToggle?.addEventListener("click", openChat);
  chatCloseBtn?.addEventListener("click", closeChat);
  chatBackdrop?.addEventListener("click", (e) => {
    if (e.target === chatBackdrop) closeChat();
  });

  // ---- Función para agregar mensajes ----
  function appendMessage(text, who = "user") {
    if (!chatBody) return;
    const div = document.createElement("div");
    div.className = `msg ${who}`;
    div.textContent = text;
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  // ---- Enviar mensaje de TEXTO al backend ----
  async function sendTextMessage(text) {
    if (!text || !text.trim()) return;

    appendMessage(text, "user");
    appendMessage("🤖 Pensando...", "bot");

    try {
      const response = await fetch(`${BACKEND_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text }),
      });

      if (!response.ok) {
        throw new Error(`Error del servidor: ${response.status}`);
      }

      const data = await response.json();
      console.log("✅ Respuesta recibida:", data);

      // Eliminar el mensaje de "Pensando..."
      const lastMsg = chatBody.lastChild;
      if (lastMsg && lastMsg.textContent.includes("Pensando")) {
        chatBody.removeChild(lastMsg);
      }

      // Mostrar respuesta
      appendMessage(data.text, "bot");

      // Reproducir audio si está disponible
      if (data.audio_base64) {
        playAudioResponse(data.audio_base64);
      }
    } catch (error) {
      console.error("❌ Error:", error);
      const lastMsg = chatBody.lastChild;
      if (lastMsg && lastMsg.textContent.includes("Pensando")) {
        chatBody.removeChild(lastMsg);
      }
      appendMessage(
        "❌ Error al conectar con el servidor. Verifica que el backend esté corriendo en " +
          BACKEND_URL,
        "bot"
      );
    }
  }

  function sendChat() {
    const text = (chatInput?.value || "").trim();
    if (!text) return;
    sendTextMessage(text);
    if (chatInput) chatInput.value = "";
  }

  chatSendBtn?.addEventListener("click", sendChat);
  chatInput?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendChat();
  });

  // ---- Arrastrar ventana (desktop) ----
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
    if (!isDragging) return;
    isDragging = false;
    document.body.style.userSelect = "";
  });

  // =========================================================
  // ---- MODO VOZ (GRABACIÓN + ENVÍO + REPRODUCCIÓN) ----
  // =========================================================
  let audioCtx, analyser, micStream, dataArray, rafId;
  let mediaRecorder,
    audioChunks = [];

  async function startVoice() {
    try {
      // Pedir permiso y stream
      micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const src = audioCtx.createMediaStreamSource(micStream);
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      const bufferLength = analyser.frequencyBinCount;
      dataArray = new Uint8Array(bufferLength);
      src.connect(analyser);

      // 🎙️ Iniciar grabación
      audioChunks = [];
      mediaRecorder = new MediaRecorder(micStream);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        console.log("🎤 Grabación detenida, enviando audio al backend...");
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        await sendAudioToBackend(audioBlob);
      };

      mediaRecorder.start();
      console.log("🎤 Grabación iniciada...");

      voiceOverlay?.classList.remove("hidden");
      drawWaves();
    } catch (err) {
      alert("No se pudo acceder al micrófono. Verifica los permisos.");
      console.error(err);
    }
  }

  async function sendAudioToBackend(audioBlob) {
    try {
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");

      appendMessage("🎤 Procesando tu audio...", "bot");

      const response = await fetch(`${BACKEND_URL}/ask`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Error del servidor: ${response.status}`);
      }

      const data = await response.json();
      console.log("✅ Respuesta de audio recibida:", data);

      // Eliminar mensaje de "Procesando"
      const lastMsg = chatBody.lastChild;
      if (lastMsg && lastMsg.textContent.includes("Procesando")) {
        chatBody.removeChild(lastMsg);
      }

      // Mostrar respuesta
      appendMessage(data.text, "bot");

      // Reproducir audio de respuesta
      if (data.audio_base64) {
        playAudioResponse(data.audio_base64);
      }
    } catch (error) {
      console.error("❌ Error al enviar audio:", error);
      const lastMsg = chatBody.lastChild;
      if (lastMsg && lastMsg.textContent.includes("Procesando")) {
        chatBody.removeChild(lastMsg);
      }
      appendMessage(
        "❌ Error al procesar el audio. Verifica que el backend esté corriendo.",
        "bot"
      );
    }
  }

  function playAudioResponse(base64Audio) {
    try {
      const audio = new Audio(`data:audio/mp3;base64,${base64Audio}`);
      audio.play();
      console.log("🔊 Reproduciendo respuesta de audio...");
    } catch (error) {
      console.error("❌ Error al reproducir audio:", error);
    }
  }

  function stopVoice() {
    cancelAnimationFrame(rafId);

    // Detener grabación
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }

    if (micStream) micStream.getTracks().forEach((t) => t.stop());
    if (audioCtx) audioCtx.close();
    micStream = null;
    audioCtx = null;
    analyser = null;
    voiceOverlay?.classList.add("hidden");
  }

  function drawWaves() {
    if (!voiceCanvas) return;
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
  inlineMicBtn?.addEventListener("click", startVoice);
  voiceStopBtn?.addEventListener("click", stopVoice);
  voiceOverlay?.addEventListener("click", (e) => {
    if (e.target === voiceOverlay) stopVoice();
  });
})();
