import os
import json
import google.generativeai as genai
from modules.prophet_engine import get_kpis, predict_serie

# ==========================
# ⚙️ Configuración de Gemini
# ==========================

print("🧠 [INIT] Cargando módulo gemini_engine desde:", __file__)

GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_KEY:
    print("⚠️  [CONFIG] Falta GEMINI_API_KEY en entorno")
else:
    print("✅ [CONFIG] GEMINI_API_KEY detectada:", GEMINI_KEY[:8] + "********")
    genai.configure(api_key=GEMINI_KEY)

# Usa el modelo correcto (sin 'models/')
MODEL_NAME = "gemini-2.5-pro"
print(f"🧩 [MODEL] Intentando inicializar modelo: {MODEL_NAME}")

try:
    MODEL = genai.GenerativeModel(MODEL_NAME)
    print(f"✅ [MODEL] Modelo '{MODEL_NAME}' inicializado correctamente.")
except Exception as e:
    print(f"❌ [MODEL INIT ERROR] No se pudo inicializar el modelo '{MODEL_NAME}': {e}")
    MODEL = None

# ==========================
# 🔍 Verificación inicial (conexión de prueba)
# ==========================
if MODEL:
    try:
        print("🧪 [TEST] Enviando prueba a Gemini...")
        test_resp = MODEL.generate_content("Hola, Gemini. Prueba de conexión del servidor financiero.")
        if test_resp and hasattr(test_resp, "text"):
            print("✅ [TEST] Conexión con Gemini OK. Respuesta:", test_resp.text[:80], "...")
        else:
            print("⚠️ [TEST] Gemini respondió sin texto. Revisa tu cuota o el modelo.")
    except Exception as e:
        print(f"🚨 [Gemini Startup Error] {e}")
else:
    print("⚠️ [INIT] No se pudo crear instancia de Gemini; modelo es None.")

# ==========================
# 🧠 Función principal
# ==========================
def ask_gemini(question: str) -> str:
    """Genera una respuesta en contexto financiero usando Gemini + Prophet."""
    print(f"\n💬 [ASK] Recibida pregunta: {question}")

    kpis_macro = get_kpis()
    forecast_hint = ""

    # --------------------------
    # 🔎 Intentar incluir contexto de predicciones
    # --------------------------
    try:
        if "tipo de cambio" in question.lower():
            preds = predict_serie("tipo_cambio_fix")
            if isinstance(preds, list) and preds:
                last = preds[-1]
                forecast_hint = f"El tipo de cambio se estima en {last['yhat']:.2f} MXN/USD para {last['ds']}."
        elif "tasa" in question.lower():
            preds = predict_serie("tasa_referencia")
            if isinstance(preds, list) and preds:
                last = preds[-1]
                forecast_hint = f"La tasa de referencia podría ser {last['yhat']:.2f}% para {last['ds']}."
        elif "ipc" in question.lower():
            preds = predict_serie("ipc_bmv")
            if isinstance(preds, list) and preds:
                last = preds[-1]
                forecast_hint = f"El IPC de la Bolsa Mexicana se estima en {last['yhat']:.2f} puntos para {last['ds']}."
    except Exception as e:
        print(f"[Gemini Context Error] {e}")

    # --------------------------
    # 📋 Crear contexto para Gemini
    # --------------------------
    context = f"""
    Contexto macroeconómico:
    {json.dumps(kpis_macro, indent=2, ensure_ascii=False)}

    {forecast_hint if forecast_hint else "Sin pronósticos recientes disponibles."}
Instrucciones:
    - Responde en español con base exclusivamente en los datos proporcionados por Prophet.
    - No inventes cifras adicionales ni amplíes rangos.
    - Si existe un valor estimado (`forecast_hint`), utilízalo como el pronóstico principal.
    - Explica brevemente el razonamiento financiero detrás, pero sin modificar la cifra estimada.
    - Usa tono de asesor financiero profesional.
    - Mantén la respuesta concisa (máximo 3 párrafos cortos).

    """

    # --------------------------
    # 🧠 Llamar a Gemini
    # --------------------------
    if MODEL is None:
        print("🚨 [ERROR] No hay modelo Gemini inicializado. Revisa configuración.")
        return "Error interno: Gemini no está configurado correctamente."

    try:
        print("📤 [Gemini Request] Enviando prompt al modelo...")
        response = MODEL.generate_content(context + "\n\nPregunta: " + question)
        print("📥 [Gemini Response] Respuesta recibida correctamente.")
        print("🧾 [Gemini Output] Primeras líneas de respuesta:\n", response.text[:200])
        print(f"[DEBUG] forecast_hint usado: {forecast_hint}")
        return response.text.strip()
    except Exception as e:
        print(f"🚨 [Gemini Error] {e}")
        return "Lo siento, no pude generar una respuesta en este momento."
