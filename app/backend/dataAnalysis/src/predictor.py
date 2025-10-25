from prophet import Prophet
import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed/macro_dataset.csv")

def predict_serie(serie: str, periods=90):
    df = pd.read_csv(DATA_PATH, parse_dates=["fecha"])
    if serie not in df.columns:
        raise ValueError(f"Serie '{serie}' no encontrada en macro_dataset.csv")

    ts = df[["fecha", serie]].dropna().rename(columns={"fecha": "ds", serie: "y"})
    model = Prophet()
    model.fit(ts)

    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    latest = forecast.tail(periods)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    return latest.to_dict(orient="records")
