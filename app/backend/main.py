import os
import json
import pandas as pd
from prophet import Prophet
from flask import Flask, jsonify, request
from pathlib import Path

# Gemini
import google.generativeai as genai

# ========================================
# 🔧 CONFIGURACIÓN GENERAL
# ========================================

app = Flask(__name__)

# Rutas de datos procesados
DATA_PATH = Path(__file__).parent / "dataAnalysis" / "data" / "processed"
MACRO_FILE = DATA_PATH / "macro_dataset.csv"
KPI_FILE = DATA_PATH / "kpis_macro.json"

# Carga datos
if MACRO_FILE.exists():
    macro_df = pd.read_csv(MACRO_FILE, parse_dates=["fecha"])
else:
    macro_df = pd.DataFrame()

if KPI_FILE.exists():
    kpis_macro = json.load(open(KPI_FILE, "r", encoding="utf-8"))
else:
    kpis_macro = {}

# Configura Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("⚠️  No se encontró GEMINI_API_KEY en el entorno.")

# ========================================
# 🔮 FUNCIONES DE PREDICCIÓN
# ========================================

def predict_serie(serie: str, periods=90):
    """Predice una serie temporal usando Prophet."""
    if macro_df.empty:
        return {"error": "No hay datos macroeconómicos cargados."}

    if serie not in macro_df.columns:
        return {"error": f"La serie '{serie}' no existe en macro_dataset.csv"}

    df = macro_df[["fecha", serie]].dropna().rename(columns={"fecha": "ds", serie: "y"})

    if len(df) < 10:
        return {"error": f"No hay suficientes datos para predecir '{serie}'"}

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    latest = forecast.tail(periods)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    return latest.to_dict(orient="records")


def ask_gemini(question: str, forecast_hint: str = ""):
    """Genera una respuesta con contexto macroeconómico."""
    if not GEMINI_API_KEY:
        return "Gemini no está configurado. Falta GEMINI_API_KEY."

    context = f"""
    Contexto macroeconómico:
    {json.dumps(kpis_macro, indent=2, ensure_ascii=False)}

    {forecast_hint}

    Instrucciones:
    - Responde en español.
    - Sé claro y analítico.
    - Usa tono de asesor financiero.
    - Si no hay datos suficientes, dilo claramente.
    """

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(context + "\n\nPregunta: " + question)
    return response.text

# ========================================
# 🌐 ENDPOINTS FLASK
# ========================================

@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "Backend de IA financiera activo 🚀"})

# --- KPIs Macro actuales
@app.route("/kpis", methods=["GET"])
def get_kpis():
    return jsonify(kpis_macro)

# --- Forecast de una serie específica (sin colisión de endpoint)
@app.route("/forecast/<serie>", methods=["GET"])
def forecast_serie(serie):
    preds = predict_serie(serie)
    return jsonify(preds)

# --- Forecast general (explicativo)
@app.route("/forecast", methods=["GET"])
def forecast_info():
    return jsonify({"message": "Usa /forecast/<serie> para obtener una predicción específica."})

# --- Chat financiero con Gemini + predicciones
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")

    # Detección automática de la serie pedida
    forecast_hint = ""
    if "tipo de cambio" in question.lower():
        preds = predict_serie("tipo_cambio")
        if "error" not in preds:
            last = preds[-1]
            forecast_hint = f"El tipo de cambio se estima en {last['yhat']:.2f} para {last['ds']}."
    elif "tasa" in question.lower():
        preds = predict_serie("tasa_referencia")
        if "error" not in preds:
            last = preds[-1]
            forecast_hint = f"La tasa de referencia podría ser {last['yhat']:.2f}% para {last['ds']}."

    answer = ask_gemini(question, forecast_hint)
    return jsonify({"question": question, "answer": answer, "forecast": forecast_hint})

# ========================================
# 🏁 INICIO DEL SERVIDOR
# ========================================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
