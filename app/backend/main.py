# app/backend/main.py - VERSION CON TWILIO INTELIGENTE
from __future__ import annotations
import os
import base64
import tempfile
import io
import time
from io import BytesIO
from typing import Optional, Dict, Any
from pydub import AudioSegment
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
from gtts import gTTS
import google.generativeai as genai

# === TWILIO INTEGRACIÓN ===
from twilio.rest import Client
import random
# ===========================

# === módulos internos ===
try:
    from modules.prophet_engine import get_kpis, predict_serie
except Exception as e:
    print(f"[WARNING] Prophet engine no disponible: {e}")
    def get_kpis() -> dict: return {}
    def predict_serie(_: str) -> list: return []

try:
    import modules.financial_advisor_v3_fixed as financial_advisor
    FINANCIAL_ENABLED = True
except Exception as e:
    print(f"[WARNING] Financial advisor no disponible: {e}")
    FINANCIAL_ENABLED = False

# === configuración ===
load_dotenv()
app = Flask(__name__)
CORS(app)

# Verificar API Key
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    print("❌ ERROR: GEMINI_API_KEY no está configurada en el archivo .env")
    print("   Por favor, agrega tu API key en app/backend/.env")
    exit(1)

print(f"[Config] ✅ API Key cargada: {GEMINI_KEY[:10]}...{GEMINI_KEY[-5:]}")

# Configurar Gemini con manejo de errores
genai.configure(api_key=GEMINI_KEY)

# Intentar con diferentes modelos hasta encontrar uno que funcione
MODELS_TO_TRY = [
    "gemini-1.5-flash",
    "gemini-1.5-pro", 
    "gemini-pro",
    "gemini-1.5-flash-latest",
    "gemini-2.0-flash-exp",
]

MODEL = None
MODEL_NAME = None
for model_name in MODELS_TO_TRY:
    try:
        print(f"[Gemini] 🧪 Probando modelo: {model_name}")
        test_model = genai.GenerativeModel(model_name)
        # Test rápido
        test_response = test_model.generate_content(
            "Di solo 'ok'",
            generation_config={"temperature": 0.7, "max_output_tokens": 10}
        )
        if test_response and test_response.text:
            MODEL = test_model
            MODEL_NAME = model_name
            print(f"[Gemini] ✅ Modelo funcionando: {model_name}")
            break
    except Exception as e:
        print(f"[Gemini] ⚠️ Modelo {model_name} falló: {str(e)[:100]}")
        continue

if MODEL is None:
    print("❌ ERROR: No se pudo inicializar ningún modelo de Gemini")
    print("   Verifica:")
    print("   1. Tu API key es válida")
    print("   2. Tienes acceso a la API en tu región")
    print("   3. No has excedido tu cuota")
    print("   4. Tienes conexión a internet")
    exit(1)

# === TWILIO CONFIGURACIÓN ===
TW_SID = os.getenv("TWILIO_ACCOUNT_SID")
TW_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TW_FROM = os.getenv("TWILIO_FROM")
TW_TO = os.getenv("ALERT_TO")
tw_client = None

if TW_SID and TW_TOKEN and TW_FROM and TW_TO:
    try:
        tw_client = Client(TW_SID, TW_TOKEN)
        print(f"[Twilio] ✅ Cliente configurado correctamente.")
        print(f"[Twilio] 📱 Enviará alertas a: {TW_TO}")
    except Exception as e:
        print(f"[Twilio] ⚠️ No se pudo inicializar cliente: {e}")
else:
    print("[Twilio] ⚠️ Configuración incompleta. Alertas desactivadas.")
    print(f"   SID: {'✅' if TW_SID else '❌'}")
    print(f"   TOKEN: {'✅' if TW_TOKEN else '❌'}")
    print(f"   FROM: {'✅' if TW_FROM else '❌'}")
    print(f"   TO: {'✅' if TW_TO else '❌'}")
# ==========================================================

# Cache simple
response_cache: Dict[str, str] = {}

# ==============================
# 🎤 Speech-to-Text MEJORADO
# ==============================
def speech_to_text(file_storage):
    """
    Convierte audio (.wav o .webm) a texto usando Google SpeechRecognition.
    Compatible con Windows + ffmpeg + pydub.
    """
    import traceback
    import tempfile
    from pydub import AudioSegment
    from pydub.utils import which

    # Configurar pydub para que encuentre ffmpeg
    AudioSegment.converter = which("ffmpeg")
    AudioSegment.ffmpeg = which("ffmpeg")
    AudioSegment.ffprobe = which("ffprobe")

    print(f"[DEBUG] ffmpeg path: {AudioSegment.converter}")

    r = sr.Recognizer()
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True

    try:
        # Leer datos del archivo recibido (FileStorage)
        file_storage.seek(0)
        audio_data = file_storage.read()
        filename = getattr(file_storage, "filename", "audio.webm")

        print(f"[STT] 📝 Archivo recibido: {filename} ({len(audio_data)} bytes)")

        # Guardar archivo temporal
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[-1], delete=False) as temp_input:
            temp_input.write(audio_data)
            temp_input_path = temp_input.name

        # Si ya es WAV, procesar directamente
        if filename.lower().endswith(".wav"):
            try:
                with sr.AudioFile(temp_input_path) as source:
                    r.adjust_for_ambient_noise(source, duration=0.3)
                    audio = r.record(source)
                text = r.recognize_google(audio, language="es-MX")
                print(f"[STT] ✅ Transcrito (WAV): {text}")
                os.unlink(temp_input_path)
                return text
            except Exception as e:
                print(f"[STT] ⚠️ Error al procesar WAV: {e}")

        # Si es WEBM u otro formato → convertir a WAV
        try:
            print("[STT] 🔄 Intentando conversión con pydub...")
            audio_segment = AudioSegment.from_file(temp_input_path, format="webm")
            audio_segment = audio_segment.set_channels(1).set_frame_rate(16000)

            temp_wav_path = temp_input_path.replace(".webm", ".wav")
            audio_segment.export(temp_wav_path, format="wav")

            with sr.AudioFile(temp_wav_path) as source:
                r.adjust_for_ambient_noise(source, duration=0.3)
                audio = r.record(source)
            text = r.recognize_google(audio, language="es-MX")

            print(f"[STT] ✅ Transcrito (pydub + ffmpeg): {text}")

            # Limpiar archivos temporales
            os.unlink(temp_input_path)
            os.unlink(temp_wav_path)

            return text
        except Exception as e:
            print(f"[STT] ❌ Error al convertir con pydub/ffmpeg: {e}")
            traceback.print_exc()
            try:
                os.unlink(temp_input_path)
            except:
                pass
            return None

    except sr.UnknownValueError:
        print("[STT] ⚠️ No se pudo entender el audio")
        return None
    except sr.RequestError as e:
        print(f"[STT] ❌ Error en servicio de Google: {e}")
        return None
    except Exception as e:
        print(f"[STT] ❌ Error general: {e}")
        traceback.print_exc()
        return None

# ==============================
# 🧠 Gemini con Análisis Financiero
# ==============================
def ask_gemini_fast(question: str) -> str:
    """Genera respuesta con análisis financiero integrado y caché inteligente."""
    question_lower = question.lower().strip()

    skip_cache = any(word in question_lower for word in ["empresa", "negocio", "estado", "cómo va", "como va"])

    if not skip_cache and question_lower in response_cache:
        print("[Gemini] 📦 Respuesta desde cache")
        return response_cache[question_lower]

    try:
        kpis = get_kpis()
    except Exception:
        kpis = {}

    forecast_hint = ""

    try:
        if "tipo de cambio" in question_lower or "dólar" in question_lower:
            preds = predict_serie("tipo_cambio_fix")
            if preds:
                last = preds[-1]
                forecast_hint = f"Tipo de cambio estimado: {last['yhat']:.2f} MXN/USD para {last['ds']}."
        elif "tasa" in question_lower or "interés" in question_lower:
            preds = predict_serie("tasa_referencia")
            if preds:
                last = preds[-1]
                forecast_hint = f"Tasa de referencia estimada: {last['yhat']:.2f}% para {last['ds']}."
    except Exception as e:
        print(f"[Prophet] ⚠️ {e}")

    financial_context = ""
    if FINANCIAL_ENABLED:
        try:
            if any(word in question_lower for word in ['empresa', 'negocio', 'ventas', 'utilidad', 'margen', 'estado', 'compañía']):
                empresa_analysis = financial_advisor.get_advisor().analyze_empresa()
                if empresa_analysis:
                    financial_context += f"""
📊 ANÁLISIS EMPRESARIAL:
- Estado: {empresa_analysis['estado']} (Score: {empresa_analysis['score']}/100)
- Margen de utilidad: {empresa_analysis['metricas']['margen_utilidad']:.1f}%
- Crecimiento trimestral: {empresa_analysis['metricas']['crecimiento_trimestral']:.1f}%
- Utilidad anual: ${empresa_analysis['metricas']['utilidad_12m']:,.0f} MXN
- {empresa_analysis['descripcion']}
"""
        except Exception as e:
            print(f"[FinAdvisor] ⚠️ Error empresarial: {e}")

    context = f"""Eres un CFO virtual experto en finanzas mexicanas. 
Responde de forma CONCISA y DIRECTA.

{financial_context}

Datos macroeconómicos: {kpis}
{forecast_hint}

Reglas:
- Máximo 4 oraciones.
- Tono profesional, pero cercano.
- En español mexicano.

Pregunta: {question}
"""

    try:
        print("[Gemini] 🧠 Generando respuesta...")
        generation_config = {
            "temperature": 0.7, 
            "max_output_tokens": 250,
            "top_p": 0.95,
            "top_k": 40
        }
        
        resp = MODEL.generate_content(context, generation_config=generation_config)
        
        if not resp or not resp.text:
            raise Exception("Respuesta vacía del modelo")
            
        answer = resp.text.strip()

        if not skip_cache:
            response_cache[question_lower] = answer
            if len(response_cache) > 100:
                response_cache.pop(next(iter(response_cache)))

        print(f"[Gemini] ✅ Respuesta generada ({len(answer)} chars)")
        return answer
        
    except Exception as e:
        import traceback
        print(f"[Gemini] ❌ Error al generar respuesta: {e}")
        traceback.print_exc()
        return "Disculpa, tuve un problema al procesar tu pregunta. Por favor, intenta de nuevo."

# ==============================
# 🔊 Text-to-Speech
# ==============================
def synthesize_voice_fast(text: str) -> Optional[str]:
    """Convierte texto a voz con gTTS."""
    try:
        print("[TTS] 🔊 Sintetizando con gTTS...")
        tts = gTTS(text=text, lang='es', slow=False, tld='com.mx')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        audio_b64 = base64.b64encode(audio_fp.read()).decode('utf-8')
        print(f"[TTS] ✅ Audio generado ({len(audio_b64)} chars base64)")
        return audio_b64
    except Exception as e:
        print(f"[TTS] ❌ Error: {e}")
        return None

# ==============================
# 📱 TWILIO - RECOMENDACIONES INTELIGENTES
# ==============================
def generate_financial_recommendation(question: str, answer: str) -> Dict[str, str]:
    """
    Genera una recomendación financiera inteligente basada en la pregunta y respuesta del bot.
    """
    question_lower = question.lower()
    answer_lower = answer.lower()
    
    # Detectar el tipo de consulta
    recommendation_type = None
    recommendation = ""
    reason = ""
    
    # 1. TIPO DE CAMBIO / DÓLAR
    if any(word in question_lower for word in ["dólar", "tipo de cambio", "usd", "cambio"]):
        if any(word in answer_lower for word in ["subir", "aumentar", "alza", "sube"]):
            recommendation_type = "💱 TIPO DE CAMBIO"
            recommendation = "COMPRAR DÓLARES 💵"
            reason = "El tipo de cambio podría subir. Es buen momento para comprar dólares si tienes pagos en USD próximamente."
        else:
            recommendation_type = "💱 TIPO DE CAMBIO"
            recommendation = "MANTENER PESOS 🇲🇽"
            reason = "El tipo de cambio está estable. No es urgente comprar dólares en este momento."
    
    # 2. INFLACIÓN
    elif any(word in question_lower for word in ["inflación", "inflacion", "precios"]):
        if any(word in answer_lower for word in ["subir", "alta", "aumentar", "incremento"]):
            recommendation_type = "📈 INFLACIÓN"
            recommendation = "AJUSTAR PRECIOS +3-5% 📊"
            reason = "La inflación está alta. Ajusta tus precios para mantener márgenes de utilidad."
        else:
            recommendation_type = "📈 INFLACIÓN"
            recommendation = "MANTENER PRECIOS 💰"
            reason = "La inflación está controlada. No es necesario ajustar precios por ahora."
    
    # 3. EMPRESA / NEGOCIO
    elif any(word in question_lower for word in ["empresa", "negocio", "estado", "cómo va", "como va"]):
        if any(word in answer_lower for word in ["bien", "bueno", "positivo", "crecimiento"]):
            recommendation_type = "🏢 TU EMPRESA"
            recommendation = "INVERTIR EN CRECIMIENTO 🚀"
            reason = "Tu empresa está en buen estado. Es momento de invertir en marketing, tecnología o expansión."
        elif any(word in answer_lower for word in ["crítico", "problema", "negativo", "bajo"]):
            recommendation_type = "🏢 TU EMPRESA"
            recommendation = "REDUCIR GASTOS URGENTE ⚠️"
            reason = "Tu empresa necesita atención. Prioriza reducción de costos y mejora de márgenes."
        else:
            recommendation_type = "🏢 TU EMPRESA"
            recommendation = "MANTENER ESTABILIDAD 📊"
            reason = "Tu empresa está estable. Monitorea indicadores y mantén las operaciones actuales."
    
    # 4. INVERSIÓN
    elif any(word in question_lower for word in ["invertir", "inversión", "inversion", "donde poner"]):
        recommendation_type = "💼 INVERSIÓN"
        recommendation = "DIVERSIFICAR: 60% CETES + 40% ACCIONES 📈"
        reason = "Estrategia equilibrada: CETES para estabilidad (11% anual) y acciones para crecimiento."
    
    # 5. CRÉDITO / PRÉSTAMO
    elif any(word in question_lower for word in ["crédito", "credito", "préstamo", "prestamo", "pedir prestado"]):
        if any(word in answer_lower for word in ["bien", "puedes", "favorable", "recomiendo"]):
            recommendation_type = "💳 CRÉDITO"
            recommendation = "SOLICITAR CRÉDITO ✅"
            reason = "Tu flujo de caja permite asumir deuda. Busca tasas menores al 15% anual."
        else:
            recommendation_type = "💳 CRÉDITO"
            recommendation = "EVITAR CRÉDITO ⚠️"
            reason = "Tu situación financiera no permite deuda adicional. Enfócate en mejorar flujo de caja primero."
    
    # 6. VENTAS / INGRESOS
    elif any(word in question_lower for word in ["ventas", "ingresos", "vender"]):
        recommendation_type = "💰 VENTAS"
        recommendation = "AUMENTAR MARKETING +20% 📣"
        reason = "Invierte más en marketing digital y promociones para incrementar ventas."
    
    # 7. GASTOS
    elif any(word in question_lower for word in ["gastos", "reducir", "ahorrar", "costos"]):
        recommendation_type = "💸 GASTOS"
        recommendation = "OPTIMIZAR GASTOS -10% 📉"
        reason = "Renegocia contratos con proveedores y elimina servicios no esenciales."
    
    # 8. FLUJO DE CAJA
    elif any(word in question_lower for word in ["flujo", "caja", "liquidez", "efectivo"]):
        if any(word in answer_lower for word in ["bien", "positivo", "saludable"]):
            recommendation_type = "💵 FLUJO DE CAJA"
            recommendation = "INVERTIR EXCEDENTES 📈"
            reason = "Tienes buen flujo. Invierte excedentes en CETES o instrumentos de bajo riesgo."
        else:
            recommendation_type = "💵 FLUJO DE CAJA"
            recommendation = "ACELERAR COBRANZA ⏰"
            reason = "Flujo ajustado. Ofrece descuentos por pronto pago y reduce plazos de cobro."
    
    # DEFAULT: Recomendación general
    else:
        recommendations = [
            {
                "type": "💼 INVERSIÓN",
                "rec": "DIVERSIFICAR CARTERA 📊",
                "reason": "Balancea entre instrumentos seguros (CETES) y de mayor rendimiento (acciones, ETFs)."
            },
            {
                "type": "📈 CRECIMIENTO",
                "rec": "REINVERTIR UTILIDADES 🚀",
                "reason": "Destina el 30% de utilidades a mejorar procesos, tecnología o expansión."
            },
            {
                "type": "⚠️ RIESGO",
                "rec": "CREAR FONDO DE EMERGENCIA 💰",
                "reason": "Mantén 3-6 meses de gastos operativos como reserva para contingencias."
            },
            {
                "type": "🎯 ESTRATEGIA",
                "rec": "REVISAR PRECIOS TRIMESTRALMENTE 📊",
                "reason": "Ajusta precios cada 3 meses considerando inflación y costos de operación."
            }
        ]
        
        choice = random.choice(recommendations)
        recommendation_type = choice["type"]
        recommendation = choice["rec"]
        reason = choice["reason"]
    
    return {
        "type": recommendation_type,
        "recommendation": recommendation,
        "reason": reason
    }

def send_twilio_smart_alert(question: str, answer: str):
    """
    Envía una alerta inteligente por Twilio con recomendación financiera basada en la conversación.
    """
    import traceback
    
    if not tw_client:
        print("[Twilio] ⚠️ Cliente no inicializado. No se enviará alerta.")
        return
    
    try:
        # Generar recomendación inteligente
        rec = generate_financial_recommendation(question, answer)
        
        # Construir mensaje
        msg_body = f"""🏦 FINCORTEX ALERT

{rec['type']}
▶ {rec['recommendation']}

💡 Motivo: {rec['reason']}

Pregunta: {question[:50]}..."""

        # Truncar si es muy largo (límite para cuentas trial)
        if len(msg_body) > 155:
            msg_body = msg_body[:152] + "..."

        print(f"[Twilio] 📱 Enviando alerta...")
        print(f"[Twilio] Mensaje ({len(msg_body)} chars):\n{msg_body}\n")

        msg = tw_client.messages.create(
            body=msg_body,
            from_=TW_FROM.strip(),
            to=TW_TO.strip()
        )

        print(f"[Twilio] ✅ Mensaje enviado!")
        print(f"[Twilio] SID: {msg.sid}")
        print(f"[Twilio] Status: {msg.status}")
        
        if msg.error_code:
            print(f"[Twilio] ⚠️ Error Code: {msg.error_code}")
            print(f"[Twilio] Error: {msg.error_message}")

    except Exception as e:
        print(f"[Twilio] ❌ Error al enviar: {e}")
        traceback.print_exc()


# ==============================
# 🌐 ENDPOINTS PRINCIPALES
# ==============================
@app.route("/")
def home() -> Any:
    return jsonify({
        "status": "ok",
        "message": "FinCortex IA con Asesor Financiero 🚀",
        "version": "3.4-twilio-smart",
        "model": MODEL_NAME,
        "twilio": "✅ Activo" if tw_client else "❌ Inactivo",
        "features": ["chat", "voice", "financial_analysis", "smart_alerts"]
    })

@app.route("/ask", methods=["POST"])
def ask() -> Any:
    """Endpoint principal con análisis financiero y alertas Twilio inteligentes."""
    start_time = time.time()
    question: Optional[str] = None

    print(f"\n{'='*60}\n[REQUEST] Nueva petición - {time.strftime('%H:%M:%S')}")

    if request.content_type and request.content_type.startswith("application/json"):
        data = request.get_json()
        question = data.get("question", "").strip()
        print(f"[TEXT] 💬 Pregunta: {question}")

    elif "audio" in request.files:
        print("[AUDIO] 🎤 Procesando audio...")
        file = request.files["audio"]
        file_bytes = BytesIO(file.read())
        file_bytes.filename = file.filename
        question = speech_to_text(file_bytes)

    if not question:
        msg = "No se pudo obtener una pregunta válida o transcribir el audio."
        print(f"[ERROR] {msg}")
        return jsonify({"error": msg}), 400

    answer = ask_gemini_fast(question)
    audio_b64 = synthesize_voice_fast(answer)
    elapsed = time.time() - start_time

    # ✅ ENVIAR ALERTA INTELIGENTE POR TWILIO
    send_twilio_smart_alert(question, answer)

    print(f"[RESPONSE] ✅ Completado en {elapsed:.2f}s\n{'='*60}\n")

    return jsonify({
        "text": answer,
        "audio_base64": audio_b64,
        "processing_time": f"{elapsed:.2f}s"
    })

# ==============================
# 📊 ENDPOINTS FINANCIEROS
# ==============================
@app.route("/api/finanzas/estado", methods=["GET"])
def get_estado() -> Any:
    if not FINANCIAL_ENABLED:
        return jsonify({"success": False, "error": "Financial advisor no disponible"}), 503
    try:
        empresa = financial_advisor.get_advisor().analyze_empresa()
        personal = financial_advisor.get_advisor().analyze_personal()
        return jsonify({"success": True, "empresa": empresa, "personal": personal})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/kpis")
def kpis() -> Any:
    try:
        return jsonify(get_kpis())
    except Exception:
        return jsonify({"error": "KPIs no disponibles"}), 503

@app.route("/forecast/<serie>")
def forecast(serie: str) -> Any:
    try:
        preds = predict_serie(serie)
        return jsonify(preds)
    except Exception:
        return jsonify({"error": "Forecast no disponible"}), 503

# ==============================
# 🚀 Run
# ==============================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 FINCORTEX VOICE v3.4 - TWILIO SMART ALERTS")
    print("⚡ MODELO ESTABLE | 🎤 Audio Full | 📱 Alertas Inteligentes")
    print("="*60)
    print(f"   - Modelo Gemini: {MODEL_NAME}")
    print(f"   - Financial Advisor: {'✅ ACTIVO' if FINANCIAL_ENABLED else '❌ DESACTIVADO'}")
    print(f"   - Twilio Alerts: {'✅ ACTIVO' if tw_client else '❌ DESACTIVADO'}")
    if tw_client:
        print(f"   - Enviará SMS a: {TW_TO}")
    print("="*60 + "\n")
    app.run(debug=False, host="0.0.0.0", port=8000, threaded=True)