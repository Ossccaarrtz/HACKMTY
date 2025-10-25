import os
from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
import requests
import uuid

app = Flask(__name__)

# Configuración de Gemini y ElevenLabs
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
AUDIO_DIR = os.getenv("AUDIO_DIR", "/app/audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Contexto y memoria conversacional
conversation_history = []

def synthesize_audio(text, filename):
    """Convierte texto en voz usando ElevenLabs"""
    voice_id = "Rachel"  # puedes cambiarlo
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.7, "similarity_boost": 0.9}
    }

    r = requests.post(url, json=data, headers=headers)
    if r.status_code == 200:
        filepath = os.path.join(AUDIO_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(r.content)
        return f"/audio/{filename}"
    else:
        print("Error en ElevenLabs:", r.text)
        return None


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_question = data.get("question", "")

    conversation_history.append({"role": "user", "content": user_question})

    # Prompt contextual para Gemini
    system_prompt = (
        "Eres FinCortex, un CFO virtual con voz profesional, empática y clara. "
        "Respondes en español a preguntas sobre finanzas, inversiones o negocios. "
        "Da explicaciones entendibles, con una conclusión práctica breve."
    )

    full_prompt = system_prompt + "\n\nHistorial:\n" + "\n".join(
        [f"{m['role'].upper()}: {m['content']}" for m in conversation_history]
    )

    # Llamada a Gemini 1.5 Pro
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    response = model.generate_content(full_prompt)

    answer = response.text if response and hasattr(response, "text") else "No pude generar respuesta."
    confidence = 0.9

    # Generar audio
    filename = f"respuesta_{uuid.uuid4().hex[:8]}.mp3"
    audio_url = synthesize_audio(answer, filename)

    conversation_history.append({"role": "assistant", "content": answer})

    return jsonify({
        "response_text": answer,
        "confidence": confidence,
        "audio_url": audio_url
    })


@app.route("/audio/<path:filename>")
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)


@app.route("/")
def home():
    return jsonify({"message": "FinCortex CFO Voice con Gemini activo"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
