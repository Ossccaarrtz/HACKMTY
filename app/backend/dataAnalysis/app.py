from flask import Flask, jsonify
import pandas as pd
import json
from pathlib import Path

app = Flask(__name__)

DATA_PATH = Path("data/processed")

def load_kpis():
    """Carga los KPIs desde los archivos procesados."""
    # JSON macro
    with open(DATA_PATH / "kpis_macro.json", "r", encoding="utf-8") as f:
        kpis_macro = json.load(f)

    # CSVs empresariales y personales
    kpis_empresas = pd.read_csv(DATA_PATH / "kpis_empresas.csv")
    kpis_personales = pd.read_csv(DATA_PATH / "kpis_personales.csv")

    return {
        "macro": kpis_macro,
        "empresas": kpis_empresas.to_dict(orient="records"),
        "personales": kpis_personales.to_dict(orient="records")
    }

@app.route("/kpis", methods=["GET"])
def get_all_kpis():
    """Devuelve todos los KPIs procesados."""
    data = load_kpis()
    return jsonify(data)

@app.route("/kpis/<string:tipo>", methods=["GET"])
def get_kpis_tipo(tipo):
    """Devuelve KPIs por tipo: macro, empresas o personales."""
    data = load_kpis()
    tipo = tipo.lower()
    if tipo in data:
        return jsonify(data[tipo])
    return jsonify({"error": "Tipo de KPI no encontrado"}), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
