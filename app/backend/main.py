# app/main.py
import os
from dotenv import load_dotenv
load_dotenv() 
from flask import Flask, request, jsonify
from flask_cors import CORS
from modules.prophet_engine import get_kpis, predict_serie
from modules.gemini_engine import ask_gemini
from modules.eleven_engine import synthesize_voice

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "MCP centralizado activo 🚀"})

@app.route("/kpis")
def kpis():
    return jsonify(get_kpis())

@app.route("/forecast/<serie>")
def forecast(serie):
    preds = predict_serie(serie)
    return jsonify(preds)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    text = ask_gemini(question)
    audio = synthesize_voice(text)
    return jsonify({"text": text, "audio_base64": audio})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
