import pandas as pd
import os
import glob

DATA_DIR = "data/externos"
OUTPUT_FILE = os.path.join(DATA_DIR, "pib_trimestral_inegi_limpio.csv")

def normalizar_periodo(p):
    """Convierte 1993|T1 o 2025|T2<P> a fecha trimestral."""
    try:
        año = int(p.split("|")[0])
        t = p.split("|")[1].replace("<P>", "").replace("<R>", "").replace("<p>", "").replace("<r>", "")
        trimestre = int(t.replace("T", "")[0])
        mes = trimestre * 3
        return pd.Timestamp(year=año, month=mes, day=1)
    except Exception:
        return pd.NaT

def limpiar_archivo(filepath):
    print(f"🧩 Procesando {os.path.basename(filepath)} ...")
    try:
        df = pd.read_csv(filepath, encoding="latin-1")
    except UnicodeDecodeError:
        df = pd.read_csv(filepath, encoding="utf-8", errors="ignore")

    # Quitar columnas vacías o extrañas
    df = df.dropna(how="all", axis=1)
    df.columns = [c.strip() for c in df.columns]

    # Unpivot: columnas -> filas
    id_col = "Descriptores"
    period_cols = [c for c in df.columns if "|" in c and "Meses" not in c and "Anual" not in c]

    df_long = df.melt(id_vars=[id_col], value_vars=period_cols,
                      var_name="periodo", value_name="valor")

    # Limpiar texto
    df_long[id_col] = (df_long[id_col]
                       .astype(str)
                       .str.encode("latin-1", errors="ignore")
                       .str.decode("utf-8", errors="ignore")
                       .str.replace(r"[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-\.,]", " ", regex=True)
                       .str.strip())

    df_long["fecha"] = df_long["periodo"].apply(normalizar_periodo)
    df_long = df_long.dropna(subset=["fecha"])
    df_long["valor"] = pd.to_numeric(df_long["valor"], errors="coerce")

    # Detectar tipo según nombre del archivo
    if "cte" in filepath.lower():
        tipo = "constante"
    elif "cor" in filepath.lower():
        tipo = "corriente"
    elif "ipim" in filepath.lower():
        tipo = "indice_fisico"
    else:
        tipo = "otro"
    df_long["tipo"] = tipo

    return df_long[["fecha", "tipo", "Descriptores", "valor"]]

def main():
    archivos = glob.glob(os.path.join(DATA_DIR, "conjunto_de_datos_pibtc_pibt_*.csv"))
    if not archivos:
        print("⚠️ No se encontraron archivos del PIB trimestral.")
        return

    todos = [limpiar_archivo(a) for a in archivos]
    df_final = pd.concat(todos, ignore_index=True)

    # Filtrar solo PIB total (B.1bP)
    df_final = df_final[df_final["Descriptores"].str.contains("Producto interno bruto", case=False, na=False)]

    df_final = df_final.sort_values(["tipo", "fecha"])
    df_final.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Archivo limpio guardado en: {OUTPUT_FILE}")
    print(df_final.head(10))

if __name__ == "__main__":
    main()
