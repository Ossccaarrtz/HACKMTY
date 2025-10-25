import requests
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BANXICO_TOKEN = os.getenv("BANXICO_TOKEN")
SERIE_ID = "SF63528"
URL = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{SERIE_ID}/datos/2020-01-01/2025-10-24?token={BANXICO_TOKEN}"

r = requests.get(URL)
r.raise_for_status()
data = r.json()

serie = data["bmx"]["series"][0]["datos"]
df = pd.DataFrame(serie)
df.rename(columns={"fecha": "fecha", "dato": "tipo_cambio"}, inplace=True)
df["tipo_cambio"] = df["tipo_cambio"].astype(float)
df.to_csv("tipo_cambio_historico.csv", index=False)

print("✅ Archivo tipo_cambio_historico.csv creado con", len(df), "registros.")
