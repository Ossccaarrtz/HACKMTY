import os
import requests
import pandas as pd
from dotenv import load_dotenv

# 🔑 Token BANXICO
load_dotenv()
TOKEN = os.getenv("BANXICO_TOKEN")

# 📂 Carpeta de salida
OUTPUT_DIR = "data/externos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 🌐 Endpoint base
BASE_URL = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/{}/datos?token={}"

# 📊 Series recomendadas adicionales
SERIES = {
    # --- Política monetaria ---
    "tiie_28d": "SF43783",           # TIIE 28 días
    "tiie_91d": "SF43784",           # TIIE 91 días
    "tasa_fondeo": "SF60653",        # Tasa de fondeo bancario
    "tasa_reportos": "SF45434",      # Tasa de reportos gubernamentales (overnight)

    # --- Crédito y sistema financiero ---
    "credito_privado_total": "SF43936",  # Crédito al sector privado total
    "captacion_bancaria_total": "SF43932",  # Captación bancaria total
    "tasa_tarjeta_credito": "SF43796",  # Tasa promedio tarjetas crédito
    "tasa_hipotecaria": "SF43795",      # Tasa promedio hipotecaria

    # --- Sector externo ---
    "tipo_cambio_interbancario": "SF43718", # Tipo de cambio interbancario 24h (spot)
    "tipo_cambio_euro": "SF60632",          # Tipo de cambio Euro/Peso
    "reservas_internacionales": "SF43707",  # Reservas internacionales semanales
    "remesas_familiares": "SF61764",        # Remesas (millones USD)

    # --- Expectativas y confianza ---
    "confianza_consumidor_banxico": "SF61745",
    "confianza_empresarial_banxico": "SF61746",

    # --- Inflación (Banxico espejo del INEGI) ---
    "inpc_general": "SP68257",
    "inpc_subyacente": "SP68263",
    "inflacion_quincenal": "SP68252",
}

def descargar_serie(nombre, serie_id):
    """Descarga una serie de Banxico y la guarda como CSV."""
    url = BASE_URL.format(serie_id, TOKEN)
    print(f"📡 Consultando {nombre} ({serie_id}) ...")

    try:
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            print(f"❌ Error HTTP {r.status_code} en {nombre}")
            return None

        data = r.json()
        if "bmx" not in data or "series" not in data["bmx"]:
            print(f"⚠️ No se encontraron datos para {nombre}")
            return None

        series = data["bmx"]["series"][0]
        if "datos" not in series or len(series["datos"]) == 0:
            print(f"⚠️ {nombre}: sin observaciones")
            return None

        df = pd.DataFrame(series["datos"])
        df.rename(columns={"fecha": "fecha", "dato": "valor"}, inplace=True)
        df["valor"] = pd.to_numeric(df["valor"].str.replace(",", ""), errors="coerce")
        df["serie_id"] = serie_id
        df["nombre"] = nombre
        df = df[["fecha", "valor", "serie_id", "nombre"]]

        path = os.path.join(OUTPUT_DIR, f"{nombre}.csv")
        df.to_csv(path, index=False)
        print(f"✅ {nombre}.csv guardado con {len(df)} registros.")
        return df

    except Exception as e:
        print(f"❌ Error en {nombre}: {e}")
        return None

def main():
    print("🚀 Descargando series adicionales de Banxico...\n")
    for nombre, serie_id in SERIES.items():
        descargar_serie(nombre, serie_id)
    print("\n✅ Descarga completada.")

if __name__ == "__main__":
    main()
