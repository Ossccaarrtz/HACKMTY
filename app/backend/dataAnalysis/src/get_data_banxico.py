import requests
import pandas as pd
import os
from dotenv import load_dotenv

# -------------------------------------
# 🔧 CONFIGURACIÓN INICIAL
# -------------------------------------
load_dotenv()
BANXICO_TOKEN = os.getenv("BANXICO_TOKEN")

# Crear carpeta si no existe
os.makedirs("data/externos", exist_ok=True)

# -------------------------------------
# 🧩 SERIES CLAVE DE BANXICO
# -------------------------------------
series_banxico = {
    # Tipo de cambio y política monetaria
    "tipo_cambio_fix": "SF43718",              # Tipo de cambio FIX USD/MXN
    "tipo_cambio_historico": "SF63528",        # Tipo de cambio histórico
    "tasa_referencia": "SF61745",              # Tasa de interés objetivo Banxico
    "udis": "SP68257",                         # Valor UDI (inflación indexada)
    
    # Instrumentos financieros y mercado
    "cetes_28d": "SF43783",                    # CETES a 28 días
    "ipc_bmv": "SF60653",                      # Índice de Precios y Cotizaciones BMV
    "reservas_internacionales": "SF43707"      # Reservas internacionales (millones USD)
}

# -------------------------------------
# 🚀 FUNCIÓN DE DESCARGA
# -------------------------------------
def descargar_serie(nombre, serie_id):
    try:
        url = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{serie_id}/datos/2020-01-01/2025-10-24?token={BANXICO_TOKEN}"
        print(f"📡 Consultando {nombre} ...")
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()

        serie = data["bmx"]["series"][0]["datos"]
        if not serie:
            print(f"⚠️  {nombre}: No se recibieron datos.")
            return

        # Crear DataFrame y limpiar valores
        df = pd.DataFrame(serie)
        df.columns = ["fecha", nombre]

        # 🔥 Limpieza: eliminar comas, convertir a float
        df[nombre] = df[nombre].astype(str).str.replace(',', '').astype(float)

        # Guardar CSV
        path = f"data/externos/{nombre}.csv"
        df.to_csv(path, index=False)
        print(f"✅  {nombre}.csv guardado con {len(df)} registros.")
    except Exception as e:
        print(f"❌ Error descargando {nombre}: {e}")

# -------------------------------------
# 🏁 EJECUTAR DESCARGAS
# -------------------------------------
if __name__ == "__main__":
    print("🚀 Descargando datasets de Banxico...\n")
    for nombre, serie_id in series_banxico.items():
        descargar_serie(nombre, serie_id)
    print("\n🎉 Descarga completada. Todos los CSV están en data/externos/")
