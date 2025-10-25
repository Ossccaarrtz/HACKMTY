import pandas as pd
import numpy as np
import os

INPUT_PATH = "data/processed/macro_dataset.csv"
OUTPUT_PATH = "data/processed/macro_features.csv"

def preprocess_macro_dataset(path=INPUT_PATH):
    print("🚀 Iniciando generación de features macroeconómicos...\n")

    df = pd.read_csv(path, parse_dates=["fecha"])
    df = df.sort_values("fecha").reset_index(drop=True)

    # --- 1️⃣ Rellenar valores faltantes de forma ligera ---
    df = df.interpolate(method="linear", limit_direction="both")

    # --- 2️⃣ Calcular variaciones porcentuales mensuales ---
    pct_change = df.set_index("fecha").pct_change() * 100
    pct_change.columns = [f"{c}_pct" for c in pct_change.columns]
    pct_change.reset_index(inplace=True)

    # --- 3️⃣ Calcular rezagos (lags) ---
    lags = {}
    for lag in [1, 3, 6]:
        lagged = df.set_index("fecha").shift(lag)
        lagged.columns = [f"{c}_lag{lag}" for c in lagged.columns]
        lags[lag] = lagged.reset_index()

    # --- 4️⃣ Combinar todas las transformaciones ---
    features = df.copy()
    for lag_df in lags.values():
        features = features.merge(lag_df, on="fecha", how="left")
    features = features.merge(pct_change, on="fecha", how="left")

    # --- 5️⃣ Crear tasas derivadas ---
    if {"tasa_referencia", "inpc_general"}.issubset(df.columns):
        features["tasa_real"] = df["tasa_referencia"] - df["inpc_general"].pct_change() * 100

    if {"tiie_28d", "inpc_general"}.issubset(df.columns):
        features["tiie_real"] = df["tiie_28d"] - df["inpc_general"].pct_change() * 100

    # --- 6️⃣ Eliminar filas iniciales con NaN por rezagos ---
    features = features.dropna().reset_index(drop=True)

    # --- 7️⃣ Exportar ---
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    features.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ Features generadas y guardadas en: {OUTPUT_PATH}")
    print(f"📊 Registros: {len(features)} | Variables: {len(features.columns)}")

    return features

if __name__ == "__main__":
    preprocess_macro_dataset()
