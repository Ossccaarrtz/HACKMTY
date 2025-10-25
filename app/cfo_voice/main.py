from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import google.generativeai as genai
import speech_recognition as sr
from pydub import AudioSegment
from dotenv import load_dotenv
import base64

# ==========================
# ⚙️ Configuración inicial
# ==========================
load_dotenv()
app = Flask(__name__)
CORS(app)

AUDIO_DIR = os.getenv("AUDIO_DIR", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
print(f"[DEBUG] GEMINI_KEY loaded: {bool(GEMINI_KEY)}")

ELEVEN_KEY = os.getenv("ELEVEN_API_KEY")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5000")

# Configurar Gemini
genai.configure(api_key=GEMINI_KEY)
MODEL = genai.GenerativeModel("models/gemini-1.5-flash")  # modelo soportado

VOICE_ID_RACHEL = "21m00Tcm4TlvDq8ikWAM"
ELEVEN_TTS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID_RACHEL}"

# ==========================
# 🧠 Gemini (texto → respuesta con datos reales)
# ==========================
def get_gemini_response(question: str) -> str:
    """Consulta el backend financiero y genera una respuesta con contexto real"""
    forecast_hint = ""

    # Detectar tipo de pregunta y consultar el backend
    try:
        if "tipo de cambio" in question.lower():
            r = requests.get(f"{BACKEND_URL}/forecast/tipo_cambio_fix", timeout=10)
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                last = data[-1]
                forecast_hint = f"El tipo de cambio se estima en {last['yhat']:.2f} MXN/USD para {last['ds']}."

        elif "tasa" in question.lower():
            r = requests.get(f"{BACKEND_URL}/forecast/tasa_referencia", timeout=10)
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                last = data[-1]
                forecast_hint = f"La tasa de referencia podría ser {last['yhat']:.2f}% para {last['ds']}."

        elif "ipc" in question.lower():
            r = requests.get(f"{BACKEND_URL}/forecast/ipc_bmv", timeout=10)
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                last = data[-1]
                forecast_hint = f"El IPC de la Bolsa Mexicana se estima en {last['yhat']:.2f} puntos para {last['ds']}."
    except Exception as e:
        print(f"[Backend Error] {e}")

    # Prompt contextual para Gemini
    prompt = f"""
    Contexto económico actual:
    {forecast_hint if forecast_hint else "Sin pronósticos recientes disponibles."}

    Pregunta del usuario: {question}

    Instrucciones:
    - Responde en español, de forma clara y ejecutiva.
    - Usa tono de asesor financiero.
    - Si hay datos de predicción, coméntalos en el análisis.
    """

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
# 🔊 ElevenLabs (texto → voz en memoria)
# ==========================
def synthesize_voice(text: str) -> str:
    """Convierte texto a voz (base64, no guarda archivos)"""
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

        # Codificar audio binario en Base64 (no se guarda en disco)
        audio_base64 = base64.b64encode(r.content).decode("utf-8")
        return audio_base64
    except Exception as e:
        print(f"[TTS Error] {e}")
        return None

# ==========================
# 🌐 Endpoint /ask
# ==========================
@app.route("/ask", methods=["POST"])
def ask():
    question = None

    # Pregunta en texto
    if request.content_type.startswith("application/json"):
        data = request.get_json()
        question = data.get("question", "").strip()

    # Pregunta en audio
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

    # Generar respuesta
    answer = get_gemini_response(question)

    # Generar voz sin guardar archivo
    audio_base64 = synthesize_voice(answer)

    return jsonify({
        "question": question,
        "text": answer,
        "audio_base64": audio_base64
    })

# ==========================
# 🏁 Inicio del servidor
# ==========================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
