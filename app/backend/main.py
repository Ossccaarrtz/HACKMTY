from flask import Flask, jsonify, request
import pandas as pd
from prophet import Prophet
import google.generativeai as genai
import os

# Configura Flask
app = Flask(__name__)

# Configura Gemini con la API key desde variables de entorno (.env)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@app.route("/forecast")
def forecast():
    """
    Endpoint de ejemplo que simula una predicción básica.
    """
    return jsonify({
        "usd_mxn_forecast": 18.2,
        "inflacion": 4.3,
        "status": "ok"
    })

@app.route("/ask", methods=["POST"])
def ask():
    """
    Endpoint para probar integración con Gemini.
    Recibe una pregunta y devuelve la respuesta del modelo.
    """
    data = request.get_json()
    question = data.get("question", "¿Qué opinas del dólar hoy?")
    
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(question)

        return jsonify({
            "question": question,
            "response": response.text,
            "status": "ok"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


@app.route("/health")
def health():
    """
    Endpoint de estado del servicio.
    """
    return jsonify({"message": "Backend AI activo"}), 200


if __name__ == "__main__":
    # Mantiene el servidor Flask corriendo dentro del contenedor
    app.run(host="0.0.0.0", port=5000)

