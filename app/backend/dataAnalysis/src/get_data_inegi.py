import requests
import pandas as pd
import os
from datetime import datetime

TOKEN = "f70ef9c9-eb49-4d81-8c1e-e14dc398968d"
BASE_URL = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/{}/es/00/true/BISE/2.0/{}/?type=json"

# Indicadores actualizados (probados en API 2.0)
INDICADORES = {
    "pib_trimestral_desestacionalizado": "6207063406",   # Producto Interno Bruto, serie desestacionalizada
    "inpc_general": "628248",                             # Índice Nacional de Precios al Consumidor general
    "inpc_subyacente": "628252",                          # INPC subyacente
    "tasa_desempleo": "381142",                           # Tasa de desocupación nacional
    "produccion_industrial": "381602",                    # Producción industrial
    "inversion_fija_bruta": "381650",                     # Inversión fija bruta
    "consumo_privado": "381654",                          # Consumo privado
    "confianza_consumidor": "381566",                     # Confianza del consumidor
    "igae": "381537",                                     # Indicador Global de la Actividad Económica
}

OUTPUT_DIR = "data/externos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def descargar_indicador(nombre, indicador_id):
    url = BASE_URL.format(indicador_id, TOKEN)
    print(f"\n📡 Consultando {nombre} ...")
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if "Data" in data and len(data["Data"]) > 0:
                df = pd.DataFrame(data["Data"])
                df.to_csv(f"{OUTPUT_DIR}/{nombre}.csv", index=False)
                print(f"✅ {nombre}.csv guardado con {len(df)} registros.")
            else:
                print(f"⚠️ {nombre}: respuesta vacía o sin campo Data.")
        else:
            print(f"❌ Error HTTP {r.status_code} en {nombre}")
    except Exception as e:
        print(f"❌ Error al procesar {nombre}: {e}")

def main():
    print("🚀 Descargando datasets del INEGI (v2.0)...\n")
    for nombre, id_indicador in INDICADORES.items():
        descargar_indicador(nombre, id_indicador)
    print("\n✅ Descarga completada.")

if __name__ == "__main__":
    main()
