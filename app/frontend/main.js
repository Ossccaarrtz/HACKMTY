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

async function fetchForecast(serie) {
  try {
    const res = await fetch(`http://127.0.0.1:8000/forecast/${serie}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.slice(-10);
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

// --- USD/MXN ---
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

// =========================================================
// CHAT FLOTANTE + VOZ IA (PUSH TO TALK)
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
  const voiceCanvas = qs("#voiceWaves");

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

  // ---- Mostrar mensajes ----
  function appendMessage(text, who = "user") {
    const div = document.createElement("div");
    div.className = `msg ${who}`;
    div.textContent = text;
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  // ---- Enviar texto ----
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

      if (data.audio_base64) {
        const audio = new Audio("data:audio/mp3;base64," + data.audio_base64);
        audio.play();
      }
    } catch (err) {
      appendMessage("Error al conectar con el servidor.", "bot");
      console.error(err);
    }
  }
  chatSendBtn?.addEventListener("click", sendChat);
  chatInput?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendChat();
  });

  // =========================================================
  // 🎙️ VOZ: PUSH TO TALK + TRANSCRIPCIÓN EN CHAT
  // =========================================================
  let mediaRecorder,
    audioChunks = [],
    currentStream = null;

  async function startVoice() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      currentStream = stream;
      audioChunks = [];
      mediaRecorder = new MediaRecorder(stream);

      voiceOverlay.classList.remove("hidden");
      appendMessage("🎙️ Escuchando... mantén presionado para hablar.", "bot");
      drawWaves(stream);

      mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);

      mediaRecorder.onstop = async () => {
        const webmBlob = new Blob(audioChunks, { type: "audio/webm" });
        const arrayBuffer = await webmBlob.arrayBuffer();
        const audioCtx = new AudioContext();
        const decoded = await audioCtx.decodeAudioData(arrayBuffer);
        const wavBuffer = audioBufferToWav(decoded);
        const wavBlob = new Blob([wavBuffer], { type: "audio/wav" });

        const formData = new FormData();
        formData.append("audio", wavBlob, "voz.wav");

        appendMessage("🤖 Analizando tu voz...", "bot");

        try {
          const res = await fetch("http://127.0.0.1:8000/ask", {
            method: "POST",
            body: formData,
          });
          const data = await res.json();

          // Mostrar la transcripción si existe
          if (data.transcription) appendMessage(data.transcription, "user");

          appendMessage(data.text || "No se obtuvo respuesta.", "bot");

          if (data.audio_base64) {
            const audio = new Audio(
              "data:audio/mp3;base64," + data.audio_base64
            );
            audio.play();
          }
        } catch (err) {
          appendMessage("Error al procesar la voz.", "bot");
          console.error(err);
        }

        stopVoice();
      };

      mediaRecorder.start();
    } catch (err) {
      alert("No se pudo acceder al micrófono.");
      console.error(err);
    }
  }

  function stopVoice() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
    }
    if (currentStream) {
      currentStream.getTracks().forEach((t) => t.stop());
      currentStream = null;
    }
    cancelAnimationFrame(rafId);
    voiceOverlay.classList.add("hidden");
  }

  // ---- Eventos push-to-talk ----
  voiceModeBtn?.addEventListener("mousedown", startVoice);
  voiceModeBtn?.addEventListener("mouseup", stopVoice);
  voiceModeBtn?.addEventListener("touchstart", startVoice);
  voiceModeBtn?.addEventListener("touchend", stopVoice);

  // 🔊 Conversión a WAV PCM16
  function audioBufferToWav(buffer) {
    const numOfChan = buffer.numberOfChannels;
    const length = buffer.length * numOfChan * 2 + 44;
    const outBuffer = new ArrayBuffer(length);
    const view = new DataView(outBuffer);
    const channels = [];
    let pos = 0;

    writeUTFBytes(view, pos, "RIFF");
    pos += 4;
    view.setUint32(pos, 36 + buffer.length * numOfChan * 2, true);
    pos += 4;
    writeUTFBytes(view, pos, "WAVE");
    pos += 4;
    writeUTFBytes(view, pos, "fmt ");
    pos += 4;
    view.setUint32(pos, 16, true);
    pos += 4;
    view.setUint16(pos, 1, true);
    pos += 2;
    view.setUint16(pos, numOfChan, true);
    pos += 2;
    view.setUint32(pos, buffer.sampleRate, true);
    pos += 4;
    view.setUint32(pos, buffer.sampleRate * 2 * numOfChan, true);
    pos += 4;
    view.setUint16(pos, numOfChan * 2, true);
    pos += 2;
    view.setUint16(pos, 16, true);
    pos += 2;
    writeUTFBytes(view, pos, "data");
    pos += 4;
    view.setUint32(pos, buffer.length * numOfChan * 2, true);
    pos += 4;

    for (let i = 0; i < buffer.numberOfChannels; i++)
      channels.push(buffer.getChannelData(i));

    let offset = 0;
    while (offset < buffer.length) {
      for (let i = 0; i < numOfChan; i++) {
        let sample = Math.max(-1, Math.min(1, channels[i][offset]));
        view.setInt16(
          pos,
          sample < 0 ? sample * 0x8000 : sample * 0x7fff,
          true
        );
        pos += 2;
      }
      offset++;
    }
    return outBuffer;
  }

  function writeUTFBytes(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }

  // ---- Ondas visuales ----
  let rafId;
  function drawWaves(stream) {
    const ctx = voiceCanvas.getContext("2d");
    const W = voiceCanvas.width,
      H = voiceCanvas.height;
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const src = audioCtx.createMediaStreamSource(stream);
    const analyser = audioCtx.createAnalyser();
    analyser.fftSize = 256;
    src.connect(analyser);
    const dataArray = new Uint8Array(analyser.frequencyBinCount);

    function loop() {
      rafId = requestAnimationFrame(loop);
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
})();
