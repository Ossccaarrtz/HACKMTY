# app/main.py - VERSION CON ASESOR FINANCIERO INTEGRADO Y DATOS REALES DE E041
import os
import base64
import tempfile
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
import google.generativeai as genai
from gtts import gTTS
import io
import time

# === módulos internos ===
from modules.prophet_engine import get_kpis, predict_serie
from modules.financial_advisor import get_advisor

# === configuración ===
load_dotenv()
app = Flask(__name__)
CORS(app)

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)
MODEL = genai.GenerativeModel("gemini-2.0-flash-exp")

# Asesor financiero
financial_advisor = get_advisor()

# Cache simple
response_cache = {}

# ==============================
# 📊 CARGA DE DATOS REALES DE EMPRESA
# ==============================
EMPRESA_ID = "E041"
DATA_PATH = os.path.join("data", "processed", "finanzas_empresa_limpio.csv")

empresa_data = None
if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
    if "empresa" in df.columns:
        empresa_data = df[df["empresa"] == EMPRESA_ID]
        print(f"[DATA] ✅ Empresa {EMPRESA_ID} cargada ({len(empresa_data)} registros)")
    else:
        print("[DATA] ⚠️ No se encontró columna 'empresa' en el CSV.")
else:
    print(f"[DATA] ⚠️ No se encontró archivo en {DATA_PATH}")

# ==============================
# 🎤 Speech-to-Text
# ==============================
def speech_to_text(file_storage):
    """Convierte audio a texto"""
    r = sr.Recognizer()
    try:
        file_storage.seek(0)
        with sr.AudioFile(file_storage) as source:
            r.adjust_for_ambient_noise(source, duration=0.3)
            audio = r.record(source)
        text = r.recognize_google(audio, language="es-MX")
        print(f"[STT] ✅ Transcrito: {text}")
        return text
    except Exception as e:
        print(f"[STT] ❌ Error: {e}")
        return None

# ==============================
# 🧠 Gemini con Análisis Financiero Real
# ==============================
def ask_gemini_fast(question: str) -> str:
    """Genera respuesta usando datos reales de la empresa E041"""
    cache_key = question.lower().strip()
    if cache_key in response_cache:
        print("[Gemini] 📦 Respuesta desde cache")
        return response_cache[cache_key]

    # Obtener KPIs macro
    try:
        kpis = get_kpis()
    except:
        kpis = {}

    # === Datos reales de empresa E041 ===
    if empresa_data is not None and not empresa_data.empty:
        resumen = empresa_data.tail(12)  # Últimos 12 registros (último año)
        ingresos = resumen["ingresos"].sum()
        gastos = resumen["gastos"].sum()
        utilidad = ingresos - gastos
        margen = (utilidad / ingresos) * 100 if ingresos > 0 else 0
        crecimiento = (resumen["ingresos"].iloc[-1] - resumen["ingresos"].iloc[0]) / resumen["ingresos"].iloc[0] * 100
        promedio_mensual = ingresos / 12

        empresa_context = f"""
📊 DATOS REALES DE EMPRESA {EMPRESA_ID}
- Ingresos últimos 12 meses: ${ingresos:,.0f} MXN
- Gastos últimos 12 meses: ${gastos:,.0f} MXN
- Utilidad neta: ${utilidad:,.0f} MXN
- Margen de utilidad: {margen:.1f}%
- Crecimiento anual estimado: {crecimiento:.2f}%
- Ingreso mensual promedio: ${promedio_mensual:,.0f} MXN
"""
    else:
        empresa_context = f"No se encontraron datos para la empresa {EMPRESA_ID}."

    # === Prompt más estructurado ===
    context = f"""
Eres un CFO virtual experto en análisis financiero mexicano. 
Tienes acceso a los datos reales de la empresa {EMPRESA_ID} y debes basar tus respuestas en ellos.

{empresa_context}

Indicadores macroeconómicos actuales: {kpis}

Reglas:
- Usa solo los datos reales de la empresa, no inventes cifras.
- Si el usuario pregunta sobre rentabilidad, márgenes o crecimiento, responde con esos valores reales.
- Si pide una recomendación, da una conclusión financiera con base en la utilidad, margen y crecimiento.
- Mantén un tono analítico, profesional y claro.
- Escribe en español mexicano.
- No repitas la pregunta.
Pregunta: {question}
"""

    try:
        print("[Gemini] 🧠 Generando respuesta con datos reales...")
        resp = MODEL.generate_content(
            context,
            generation_config={"temperature": 0.3, "max_output_tokens": 300},
        )
        answer = resp.text.strip()
        response_cache[cache_key] = answer
        print(f"[Gemini] ✅ Respuesta: {answer[:80]}...")
        return answer
    except Exception as e:
        print(f"[Gemini] ❌ Error: {e}")
        return "No pude generar una respuesta en este momento."

# ==============================
# 🔊 Text-to-Speech
# ==============================
def synthesize_voice_fast(text: str) -> str:
    """Convierte texto a voz"""
    try:
        tts = gTTS(text=text, lang='es', slow=False, tld='com.mx')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return base64.b64encode(audio_fp.read()).decode('utf-8')
    except Exception as e:
        print(f"[TTS] ❌ Error: {e}")
        return None

# ==============================
# 🌐 ENDPOINTS
# ==============================
@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "FinCortex IA con Datos Reales E041 🚀",
        "version": "3.1",
        "empresa": EMPRESA_ID
    })

@app.route("/ask", methods=["POST"])
def ask():
    """Pregunta a la IA basada en datos reales"""
    start_time = time.time()
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "No se recibió pregunta válida"}), 400

    answer = ask_gemini_fast(question)
    audio_b64 = synthesize_voice_fast(answer)
    elapsed = time.time() - start_time

    return jsonify({
        "text": answer,
        "audio_base64": audio_b64,
        "processing_time": f"{elapsed:.2f}s"
    })

# ==============================
# 🚀 Run
# ==============================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 FINCORTEX VOICE - DATOS REALES E041")
    print("📊 Usa información real de finanzas_empresa_limpio.csv")
    print("="*60 + "\n")
    app.run(debug=False, host="0.0.0.0", port=8000, threaded=True)
