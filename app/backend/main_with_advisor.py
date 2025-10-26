# app/main.py - VERSION CON ASESOR FINANCIERO INTEGRADO
import os
import base64
import tempfile
from io import BytesIO
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
import google.generativeai as genai
from gtts import gTTS
import io

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
# 🎤 Speech-to-Text
# ==============================
def speech_to_text(file_storage):
    """Convierte audio a texto"""
    try:
        from pydub import AudioSegment
    except ImportError:
        AudioSegment = None
    
    r = sr.Recognizer()
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True
    
    try:
        file_storage.seek(0)
        audio_data = file_storage.read()
        filename = getattr(file_storage, 'filename', 'audio.webm')
        
        print(f"[STT] 📝 Procesando: {filename} ({len(audio_data)} bytes)")
        
        if filename.endswith('.wav') or not AudioSegment:
            file_storage.seek(0)
            with sr.AudioFile(file_storage) as source:
                r.adjust_for_ambient_noise(source, duration=0.3)
                audio_rec = r.record(source)
            text = r.recognize_google(audio_rec, language="es-MX")
            print(f"[STT] ✅ Transcrito: {text}")
            return text
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            temp_wav_path = temp_wav.name
        with tempfile.NamedTemporaryFile(delete=False) as temp_input:
            temp_input.write(audio_data)
            temp_input_path = temp_input.name
        
        try:
            audio = AudioSegment.from_file(temp_input_path)
            audio = audio.set_channels(1).set_frame_rate(16000)
            audio.export(temp_wav_path, format='wav')
            
            with sr.AudioFile(temp_wav_path) as source:
                r.adjust_for_ambient_noise(source, duration=0.3)
                audio_rec = r.record(source)
            
            text = r.recognize_google(audio_rec, language="es-MX")
            print(f"[STT] ✅ Transcrito: {text}")
            return text
        finally:
            try:
                os.unlink(temp_input_path)
                os.unlink(temp_wav_path)
            except:
                pass
    except sr.UnknownValueError:
        print("[STT] ⚠️ Audio no entendible")
        return None
    except Exception as e:
        print(f"[STT] ❌ Error: {e}")
        return None

# ==============================
# 🧠 Gemini con Análisis Financiero
# ==============================
def ask_gemini_fast(question: str) -> str:
    """Genera respuesta con análisis financiero integrado"""
    
    cache_key = question.lower().strip()
    if cache_key in response_cache:
        print("[Gemini] 📦 Respuesta desde cache")
        return response_cache[cache_key]
    
    try:
        kpis = get_kpis()
    except:
        kpis = {}
    
    forecast_hint = ""
    question_lower = question.lower()
    
    # Prophet predictions
    if "tipo de cambio" in question_lower or "dólar" in question_lower:
        try:
            preds = predict_serie("tipo_cambio_fix")
            if preds:
                last = preds[-1]
                forecast_hint = f"Tipo de cambio estimado: {last['yhat']:.2f} MXN/USD para {last['ds']}."
        except:
            pass
    elif "tasa" in question_lower or "interés" in question_lower:
        try:
            preds = predict_serie("tasa_referencia")
            if preds:
                last = preds[-1]
                forecast_hint = f"Tasa de referencia estimada: {last['yhat']:.2f}% para {last['ds']}."
        except:
            pass
    
    # 🆕 ANÁLISIS FINANCIERO
    financial_context = ""
    
    # Análisis empresarial
    if any(word in question_lower for word in ['empresa', 'negocio', 'ventas', 'utilidad', 'margen', 'estado', 'compañía']):
        try:
            empresa_analysis = financial_advisor.analyze_empresa()
            if empresa_analysis:
                financial_context = f"""
📊 ANÁLISIS EMPRESARIAL:
- Estado: {empresa_analysis['estado']} (Score: {empresa_analysis['score']}/100)
- Margen de utilidad: {empresa_analysis['margen_utilidad']:.1f}%
- Crecimiento trimestral: {empresa_analysis['crecimiento_trimestral']:.1f}%
- Utilidad anual: ${empresa_analysis['utilidad_neta']:,.0f} MXN
- {empresa_analysis['descripcion']}

"""
        except Exception as e:
            print(f"[FinAdvisor] ❌ Error empresarial: {e}")
    
    # Análisis personal
    if any(word in question_lower for word in ['personal', 'ahorro', 'gastos', 'ingresos', 'finanzas personales']):
        try:
            personal_analysis = financial_advisor.analyze_personal()
            if personal_analysis:
                financial_context += f"""
💰 ANÁLISIS PERSONAL:
- Estado: {personal_analysis['estado']} (Score: {personal_analysis['score']}/100)
- Tasa de ahorro: {personal_analysis['tasa_ahorro']:.1f}%
- Ahorro mensual: ${personal_analysis['ahorro_mensual']:,.0f} MXN
- Ingresos mensuales: ${personal_analysis['ingresos_mensuales']:,.0f} MXN
- {personal_analysis['descripcion']}

"""
        except Exception as e:
            print(f"[FinAdvisor] ❌ Error personal: {e}")
    
    # Recomendaciones
    if any(word in question_lower for word in ['recomendacion', 'recomiend', 'suger', 'consejo', 'invertir', 'préstamo', 'crédito']):
        try:
            if any(word in question_lower for word in ['empresa', 'negocio']):
                empresa_analysis = financial_advisor.analyze_empresa()
                recs = financial_advisor.get_recomendaciones_empresa(empresa_analysis)
                if recs:
                    financial_context += "\n💡 RECOMENDACIONES TOP:\n"
                    for i, rec in enumerate(recs[:2], 1):
                        financial_context += f"{i}. **{rec['titulo']}**: {rec['descripcion']}\n"
            
            if 'personal' in question_lower or not ('empresa' in question_lower or 'negocio' in question_lower):
                personal_analysis = financial_advisor.analyze_personal()
                recs = financial_advisor.get_recomendaciones_personal(personal_analysis)
                if recs:
                    financial_context += "\n💡 RECOMENDACIONES TOP:\n"
                    for i, rec in enumerate(recs[:2], 1):
                        financial_context += f"{i}. **{rec['titulo']}**: {rec['descripcion']}\n"
        except Exception as e:
            print(f"[FinAdvisor] ❌ Error recomendaciones: {e}")
    
    # Prompt optimizado
    context = f"""Eres un CFO virtual experto en finanzas mexicanas. Responde de forma CONCISA y DIRECTA.

{financial_context}

Datos macro: {kpis}
{forecast_hint}

Reglas:
- Respuestas cortas (máximo 4 oraciones)
- Si hay análisis financiero, úsalo prominentemente
- Si hay recomendaciones, menciónalas
- Tono profesional pero amigable
- En español mexicano
- Da cifras específicas cuando las tengas

Pregunta: {question}"""

    try:
        print("[Gemini] 🧠 Generando respuesta...")
        
        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 250,
        }
        
        resp = MODEL.generate_content(context, generation_config=generation_config)
        answer = resp.text.strip()
        
        response_cache[cache_key] = answer
        if len(response_cache) > 100:
            response_cache.pop(next(iter(response_cache)))
        
        print(f"[Gemini] ✅ Respuesta: {answer[:50]}...")
        return answer
        
    except Exception as e:
        print(f"[Gemini] ❌ Error: {e}")
        return "Lo siento, no pude generar una respuesta en este momento."

# ==============================
# 🔊 Text-to-Speech
# ==============================
def synthesize_voice_fast(text: str) -> str:
    """Convierte texto a voz con gTTS"""
    try:
        print("[TTS] 🔊 Sintetizando con gTTS...")
        tts = gTTS(text=text, lang='es', slow=False, tld='com.mx')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        audio_b64 = base64.b64encode(audio_fp.read()).decode('utf-8')
        print(f"[TTS] ✅ Audio generado")
        return audio_b64
    except Exception as e:
        print(f"[TTS] ❌ Error: {e}")
        return None

# ==============================
# 🌐 ENDPOINTS PRINCIPALES
# ==============================
@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "FinCortex IA con Asesor Financiero 🚀",
        "version": "3.0-advisor",
        "features": ["chat", "voice", "financial_analysis", "recommendations"]
    })

@app.route("/ask", methods=["POST"])
def ask():
    """Endpoint principal con análisis financiero integrado"""
    import time
    start_time = time.time()
    
    question = None
    print(f"\n{'='*60}")
    print(f"[REQUEST] Nueva petición - {time.strftime('%H:%M:%S')}")
    
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
        if question:
            print(f"[AUDIO] ✅ Transcrito: {question}")

    if not question:
        return jsonify({"error": "No se recibió pregunta válida"}), 400

    answer = ask_gemini_fast(question)
    audio_b64 = synthesize_voice_fast(answer)
    
    elapsed = time.time() - start_time
    print(f"[RESPONSE] ✅ Completado en {elapsed:.2f}s")
    print(f"{'='*60}\n")

    return jsonify({
        "text": answer,
        "audio_base64": audio_b64,
        "processing_time": f"{elapsed:.2f}s"
    })

# ==============================
# 📊 ENDPOINTS DE ANÁLISIS FINANCIERO
# ==============================

@app.route("/api/finanzas/estado", methods=["GET"])
def get_estado():
    """Obtener estado financiero resumido"""
    try:
        empresa = financial_advisor.analyze_empresa()
        personal = financial_advisor.analyze_personal()
        
        return jsonify({
            'success': True,
            'empresa': {
                'estado': empresa['estado'],
                'score': empresa['score'],
                'margen': empresa['margen_utilidad'],
                'descripcion': empresa['descripcion']
            },
            'personal': {
                'estado': personal['estado'],
                'score': personal['score'],
                'tasa_ahorro': personal['tasa_ahorro'],
                'descripcion': personal['descripcion']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/finanzas/analisis", methods=["GET"])
def get_analisis():
    """Análisis financiero completo con recomendaciones"""
    try:
        resultado = financial_advisor.get_analisis_completo()
        return jsonify({'success': True, 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/finanzas/recomendaciones", methods=["GET"])
def get_recomendaciones():
    """Solo recomendaciones"""
    tipo = request.args.get('tipo', 'todas')  # empresa, personal, todas
    
    try:
        recomendaciones = {
            'empresa': [],
            'personal': []
        }
        
        if tipo in ['empresa', 'todas']:
            empresa = financial_advisor.analyze_empresa()
            recomendaciones['empresa'] = financial_advisor.get_recomendaciones_empresa(empresa)
        
        if tipo in ['personal', 'todas']:
            personal = financial_advisor.analyze_personal()
            recomendaciones['personal'] = financial_advisor.get_recomendaciones_personal(personal)
        
        return jsonify({'success': True, 'recomendaciones': recomendaciones})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/kpis")
def kpis():
    return jsonify(get_kpis())

@app.route("/forecast/<serie>")
def forecast(serie):
    preds = predict_serie(serie)
    return jsonify(preds)

# ==============================
# 🚀 Run
# ==============================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 FINCORTEX VOICE - CON ASESOR FINANCIERO v3.0")
    print("⚡ Velocidad optimizada | 🎤 Voz rápida | 📊 Análisis inteligente")
    print("="*60 + "\n")
    app.run(debug=False, host="0.0.0.0", port=8000, threaded=True)
