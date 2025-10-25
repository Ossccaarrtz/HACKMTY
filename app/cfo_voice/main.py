from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import google.generativeai as genai
import speech_recognition as sr
from pydub import AudioSegment
from dotenv import load_dotenv

# ==========================
# ⚙️ Configuración inicial
# ==========================
load_dotenv()
app = Flask(__name__)
CORS(app)

AUDIO_DIR = os.getenv("AUDIO_DIR", "/app/audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ELEVEN_KEY = os.getenv("ELEVEN_API_KEY")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-ai:5000")

genai.configure(api_key=GEMINI_KEY)
MODEL = genai.GenerativeModel("gemini-2.5-pro")

VOICE_ID_RACHEL = "21m00Tcm4TlvDq8ikWAM"
ELEVEN_TTS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID_RACHEL}"

# ==========================
# 🧠 Gemini (texto → respuesta)
# ==========================
def get_gemini_response(prompt: str) -> str:
    try:
        result = MODEL.generate_content(prompt)
        return result.text.strip()
    except Exception as e:
        print(f"[Gemini Error] {e}")
        return "Lo siento, no pude generar una respuesta en este momento."

# ==========================
# 🎧 Speech-to-Text
# ==========================
def speech_to_text(file_path: str) -> str:
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio, language="es-MX")
    except Exception as e:
        print(f"[STT Error] {e}")
        return None

# ==========================
# 🔊 ElevenLabs (texto → voz)
# ==========================
def synthesize_voice(text: str) -> str:
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_KEY
    }
    payload = {
        "text": text,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
    }

    try:
        r = requests.post(ELEVEN_TTS_URL, headers=headers, json=payload)
        if r.status_code != 200:
            print(f"[ElevenLabs Error] {r.text}")
            return None

        filename = f"resp_{len(os.listdir(AUDIO_DIR)) + 1}.mp3"
        file_path = os.path.join(AUDIO_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(r.content)
        return filename
    except Exception as e:
        print(f"[TTS Error] {e}")
        return None

# ==========================
# 🌐 Endpoint /ask
# ==========================
@app.route("/ask", methods=["POST"])
def ask():
    question = None

    if request.content_type.startswith("application/json"):
        data = request.get_json()
        question = data.get("question", "").strip()

    elif "audio" in request.files:
        audio_file = request.files["audio"]
        temp_path = os.path.join(AUDIO_DIR, "input_temp.webm")
        audio_file.save(temp_path)

        wav_path = temp_path.replace(".webm", ".wav").replace(".mp3", ".wav")
        sound = AudioSegment.from_file(temp_path)
        sound.export(wav_path, format="wav")

        question = speech_to_text(wav_path)
        os.remove(temp_path)
        os.remove(wav_path)

    if not question:
        return jsonify({"error": "No se recibió pregunta válida"}), 400

    answer = get_gemini_response(question)
    audio_filename = synthesize_voice(answer)

    return jsonify({
        "text": answer,
        "audio_url": f"/audio/{audio_filename}" if audio_filename else None
    })

@app.route("/audio/<path:filename>")
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename, mimetype="audio/mpeg")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
