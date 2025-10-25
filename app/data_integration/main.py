from flask import Flask, jsonify
import pandas as pd
from prophet import Prophet

app = Flask(__name__)

@app.route("/forecast")
def forecast():
    # Dummy ejemplo
    return jsonify({"usd_mxn_forecast": 18.2, "inflacion": 4.3})

@app.route("/health")
def health():
    return "ok", 200
