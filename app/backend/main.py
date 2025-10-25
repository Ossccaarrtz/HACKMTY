from flask import Flask, jsonify
import pandas as pd
from prophet import Prophet

app = Flask(__name__)

@app.route("/forecast")
def forecast():
    # Ejemplo básico temporal de predicción simulada
    return jsonify({
        "usd_mxn_forecast": 18.2,
        "inflacion": 4.3,
        "status": "ok"
    })

@app.route("/health")
def health():
    return jsonify({"message": "Backend AI activo"}), 200


if __name__ == "__main__":
    # Mantiene el servidor Flask corriendo dentro del contenedor
    app.run(host="0.0.0.0", port=5000)
