from flask import Flask, jsonify
import pandas as pd
from prophet import Prophet
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Data Integration activo"}), 200


@app.route("/banxico")
def banxico_data():
    """
    Ejemplo: consumir API de Banxico o fuente externa.
    Aquí devolvemos un dummy temporal.
    """
    data = {
        "tipo_cambio": 18.21,
        "fecha": "2025-10-24"
    }
    return jsonify(data)


@app.route("/simulate")
def simulate():
    """
    Ejemplo: usa Prophet para simular serie temporal simple.
    """
    df = pd.DataFrame({
        "ds": pd.date_range(start="2025-10-01", periods=5, freq="D"),
        "y": [18.1, 18.2, 18.3, 18.25, 18.22]
    })
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=3)
    forecast = model.predict(future)[["ds", "yhat"]].tail(3)
    return jsonify(forecast.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
