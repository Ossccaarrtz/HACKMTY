import os
import json
import pandas as pd
from prophet import Prophet
from pathlib import Path

# ==========================
# ⚙️ Configuración de rutas
# ==========================
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed"
MACRO_FILE = DATA_PATH / "macro_dataset_clean.csv"
KPI_FILE = DATA_PATH / "kpis_macro.json"

# ==========================
# 📈 Carga de datos
# ==========================
if MACRO_FILE.exists():
    macro_df = pd.read_csv(MACRO_FILE, parse_dates=["fecha"])
else:
    print("⚠️  No se encontró macro_dataset_clean.csv")
    macro_df = pd.DataFrame()

if KPI_FILE.exists():
    kpis_macro = json.load(open(KPI_FILE, "r", encoding="utf-8"))
else:
    print("⚠️  No se encontró kpis_macro.json")
    kpis_macro = {}

# ==========================
# 🔮 Funciones principales
# ==========================
def get_kpis():
    """Devuelve el JSON con KPIs macroeconómicos."""
    return kpis_macro

def predict_serie(serie: str, periods: int = 90):
    """Predice una serie temporal usando Prophet."""
    if macro_df.empty:
        return {"error": "No hay datos macroeconómicos cargados."}

    if serie not in macro_df.columns:
        return {"error": f"La serie '{serie}' no existe en macro_dataset_clean.csv."}

    df = macro_df[["fecha", serie]].dropna().rename(columns={"fecha": "ds", serie: "y"})
    if len(df) < 10:
        return {"error": f"No hay suficientes datos para predecir '{serie}'."}

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    latest = forecast.tail(periods)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    return latest.to_dict(orient="records")
