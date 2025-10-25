from flask import Flask, request, jsonify, send_file
import google.generativeai as genai
import requests
import speech_recognition as sr
from werkzeug.utils import secure_filename
import os
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Config
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

genai.configure(api_key=GEMINI_KEY)

VOICE_ID_RACHEL = "21m00Tcm4TlvDq8ikWAM"
TTS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID_RACHEL}"

# 🔹 Speech-to-Text
def speech_to_text(file_path):
    r = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio, language="es-MX")
    except sr.UnknownValueError:
        return None

# 🔹 Gemini consulta
def get_gemini_answer(text):
    model = genai.GenerativeModel("gemini-pro")
    resp = model.generate_content(text)
    return resp.text.strip()

# 🔹 Text-to-Speech con Rachel
def synthesize_rachel(text):
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_KEY
    }
    payload = {
        "text": text,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
    }
    r = requests.post(TTS_URL, json=payload, headers=headers)
    return r.content if r.status_code == 200 else None


# ============================
# 🗣 1️⃣ Texto o Voz a Voz
# ============================
@app.route("/ask", methods=["POST"])
def ask():
    """
    Acepta:
      - {question: "..."} para texto
      - o archivo de audio multipart/form
    Devuelve:
      - JSON con texto y url del audio
    """
    question = None
    if request.content_type.startswith("application/json"):
        question = request.json.get("question", "").strip()
    elif "audio" in request.files:
        audio_file = request.files["audio"]
        filename = secure_filename(audio_file.filename)
        path = os.path.join(UPLOAD_DIR, filename)
        audio_file.save(path)
        question = speech_to_text(path)
        os.remove(path)

    if not question:
        return jsonify({"error": "No se recibió pregunta"}), 400

    # Gemini responde
    answer = get_gemini_answer(question)

    # ElevenLabs genera voz
    audio_bytes = synthesize_rachel(answer)
    if not audio_bytes:
        return jsonify({"error": "Falla generando audio"}), 500

    audio_path = os.path.join(UPLOAD_DIR, f"resp_{len(os.listdir(UPLOAD_DIR))}.mp3")
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)

    return jsonify({
        "text": answer,
        "audio_url": f"/audio/{os.path.basename(audio_path)}"
    })


# ============================
# 🔉 Servir audios generados
# ============================
@app.route("/audio/<fname>")
def get_audio(fname):
    return send_file(os.path.join(UPLOAD_DIR, fname), mimetype="audio/mpeg")


if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0", debug=True)
