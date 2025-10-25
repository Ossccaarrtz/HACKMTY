# app/main.py
import os
import base64
from io import BytesIO
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
import requests
import google.generativeai as genai

# === módulos internos ===
from modules.prophet_engine import get_kpis, predict_serie

# === configuración ===
load_dotenv()
app = Flask(__name__)
CORS(app)

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")

genai.configure(api_key=GEMINI_KEY)
MODEL = genai.GenerativeModel("gemini-2.5-pro")

VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel (ElevenLabs)
TTS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

# ==============================
# 🎤 Speech-to-Text (WAV directo)
# ==============================
def speech_to_text(file_storage):
    """Convierte audio WAV recibido (FileStorage o BytesIO) en texto."""
    r = sr.Recognizer()
    with sr.AudioFile(file_storage) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio, language="es-MX")
        print(f"[STT] Transcripción: {text}")
        return text
    except Exception as e:
        print(f"[STT ERROR] {e}")
        return None

# ==============================
# 🧠 Gemini + Prophet
# ==============================
def ask_gemini(question: str) -> str:
    """Genera respuesta financiera usando Gemini y Prophet."""
    kpis = get_kpis()
    forecast_hint = ""

    # Integración con Prophet
    try:
        if "tipo de cambio" in question.lower():
            preds = predict_serie("tipo_cambio_fix")
            if preds:
                last = preds[-1]
                forecast_hint = f"El tipo de cambio estimado es {last['yhat']:.2f} MXN/USD para {last['ds']}."
        elif "tasa" in question.lower():
            preds = predict_serie("tasa_referencia")
            if preds:
                last = preds[-1]
                forecast_hint = f"La tasa de referencia estimada es {last['yhat']:.2f}% para {last['ds']}."
    except Exception as e:
        print("[Prophet Error]", e)

    context = f"""
    Datos macroeconómicos recientes:
    {kpis}

    {forecast_hint if forecast_hint else "Sin datos predictivos disponibles."}

    Instrucciones:
    - Responde en español con base exclusivamente en los datos proporcionados por Prophet.
    - No inventes cifras adicionales.
    - Si existe un valor estimado (`forecast_hint`), utilízalo como pronóstico principal.
    - Explica brevemente el razonamiento financiero detrás, pero sin modificar la cifra estimada.
    - Usa tono de asesor financiero profesional.
    """

    try:
        print("[Gemini] Generando respuesta...")
        resp = MODEL.generate_content(context + "\n\nPregunta: " + question)
        return resp.text.strip()
    except Exception as e:
        print("[Gemini Error]", e)
        return "No se pudo generar respuesta con Gemini."

# ==============================
# 🔊 Text-to-Speech (en memoria)
# ==============================
def synthesize_voice(text: str) -> str:
    """Convierte texto en voz y devuelve audio en base64 (sin guardar archivo)."""
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
        r = requests.post(TTS_URL, json=payload, headers=headers)
        if r.status_code == 200:
            return base64.b64encode(r.content).decode("utf-8")
        else:
            print("[TTS Error]", r.text)
            return None
    except Exception as e:
        print("[TTS Exception]", e)
        return None

# ==============================
# 🧠 ENDPOINTS
# ==============================
@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "FinCortex IA Activa 🚀"})

@app.route("/kpis")
def kpis():
    return jsonify(get_kpis())

@app.route("/forecast/<serie>")
def forecast(serie):
    preds = predict_serie(serie)
    return jsonify(preds)

@app.route("/ask", methods=["POST"])
def ask():
    """
    Acepta:
      - JSON {"question": "..."}
      - o multipart/form con 'audio' (WAV)
    Devuelve:
      - texto generado + audio en base64
    """
    question = None

    if request.content_type and request.content_type.startswith("application/json"):
        data = request.get_json()
        question = data.get("question", "").strip()

    elif "audio" in request.files:
        file = request.files["audio"]
        file_bytes = BytesIO(file.read())
        question = speech_to_text(file_bytes)

    if not question:
        return jsonify({"error": "No se recibió pregunta válida"}), 400

    print(f"💬 Pregunta: {question}")

    answer = ask_gemini(question)
    audio_b64 = synthesize_voice(answer)

    return jsonify({
        "text": answer,
        "audio_base64": audio_b64
    })

# ==============================
# 🚀 Run
# ==============================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
