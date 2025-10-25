import os
import pandas as pd
from glob import glob

# 📂 Directorio donde están tus CSVs
INPUT_DIR = "data/externos"
OUTPUT_DIR = "data/processed"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_and_clean_csv(path):
    """Carga un CSV y lo estandariza a formato (fecha, valor, nombre_columna)"""
    name = os.path.basename(path).replace(".csv", "")
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except Exception:
        df = pd.read_csv(path, encoding="latin-1")

    # Normalizar columnas de fecha
    fecha_col = None
    for c in df.columns:
        if "fecha" in c.lower() or "date" in c.lower():
            fecha_col = c
            break

    if not fecha_col:
        print(f"⚠️ {name}: no se encontró columna de fecha.")
        return None

    df[fecha_col] = pd.to_datetime(df[fecha_col], errors="coerce")

    # Si tiene columna 'valor', úsala
    if "valor" in df.columns:
        df = df[[fecha_col, "valor"]].rename(columns={"valor": name})
    else:
        # Buscar la primera columna numérica
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            df = df[[fecha_col, numeric_cols[0]]].rename(columns={numeric_cols[0]: name})
        else:
            print(f"⚠️ {name}: sin datos numéricos detectados.")
            return None

    # Eliminar duplicados y ordenar
    df = df.drop_duplicates(subset=[fecha_col]).sort_values(fecha_col)
    df = df.groupby(fecha_col).mean(numeric_only=True).reset_index()

    # Renombrar la columna de fecha
    df = df.rename(columns={fecha_col: "fecha"})
    return df

def merge_all_monthly(input_dir=INPUT_DIR):
    """Combina todos los CSV en una sola base mensual"""
    files = glob(os.path.join(input_dir, "*.csv"))
    print(f"📂 Archivos detectados: {len(files)}")

    merged_df = None

    for f in files:
        df = load_and_clean_csv(f)
        if df is None or df.empty:
            continue

        # Convertir a frecuencia mensual
        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.set_index("fecha").resample("M").mean().reset_index()

        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on="fecha", how="outer")

    # Ordenar por fecha
    merged_df = merged_df.sort_values("fecha").reset_index(drop=True)

    # Exportar
    output_path = os.path.join(OUTPUT_DIR, "macro_dataset.csv")
    merged_df.to_csv(output_path, index=False)
    print(f"\n✅ Dataset combinado guardado en: {output_path}")
    print(f"📊 Registros: {len(merged_df)} | Variables: {len(merged_df.columns)}")

    return merged_df

if __name__ == "__main__":
    print("🚀 Comenzando combinación mensual de datasets macroeconómicos...\n")
    merge_all_monthly()
