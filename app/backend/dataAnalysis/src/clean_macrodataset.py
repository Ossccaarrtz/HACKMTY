import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed/macro_dataset.csv")
OUT_PATH = Path("data/processed/macro_dataset_clean.csv")

# Cargar dataset
df = pd.read_csv(DATA_PATH)

# 1️⃣ Asegurar formato de fecha
df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

# 2️⃣ Interpolar valores faltantes por columna numérica
for col in df.columns:
    if df[col].dtype != "O":
        df[col] = df[col].interpolate(limit_direction="both")

# 3️⃣ Eliminar filas completamente vacías
df = df.dropna(how="all")

# 4️⃣ Reordenar por fecha
df = df.sort_values("fecha")

# 5️⃣ Guardar limpio
df.to_csv(OUT_PATH, index=False)
print("✅ Dataset limpio guardado en:", OUT_PATH)
