document.getElementById("askBtn").addEventListener("click", async () => {
  const question = document.getElementById("question").value.trim();
  const responseDiv = document.getElementById("response");
  const audioPlayer = document.getElementById("voicePlayer");

  if (!question) {
    responseDiv.innerHTML = "Por favor escribe una pregunta.";
    return;
  }

  responseDiv.innerHTML = "💬 Pensando...";
  audioPlayer.style.display = "none";

  try {
    const res = await fetch("http://localhost:8000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const data = await res.json();
    responseDiv.innerHTML = `<b>Respuesta del CFO:</b><br>${data.text}`;

    if (data.audio_url) {
      audioPlayer.src = `http://localhost:8000${data.audio_url}`;
      audioPlayer.style.display = "block";
      audioPlayer.play();
    }
  } catch {
    responseDiv.innerHTML = "❌ Error conectando con el CFO Virtual.";
  }
});
