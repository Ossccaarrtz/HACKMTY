import pandas as pd
from pathlib import Path
import json

# ===========================================
# 🧩 FIX PIB LIMPIO – FINCORTEX / HACKMTY
# ===========================================

pib_path = Path("data/externos/pib_trimestral_inegi_limpio.csv")
if not pib_path.exists():
    raise FileNotFoundError("❌ No se encontró pib_trimestral_inegi_limpio.csv")

df = pd.read_csv(pib_path)
df.columns = [c.strip().lower() for c in df.columns]

# Detectar columnas
fecha_col = [c for c in df.columns if "fecha" in c][0]
valor_col = [c for c in df.columns if "valor" in c][0]
desc_col = [c for c in df.columns if "descrip" in c][0]

df[fecha_col] = pd.to_datetime(df[fecha_col], errors="coerce")

# 🔍 Filtrar SOLO los valores en millones de pesos
mask = df[desc_col].str.contains("Millones de pesos", case=False, na=False)
df_pib = df[mask].copy()

# Convertir a número
df_pib[valor_col] = pd.to_numeric(
    df_pib[valor_col].astype(str).str.replace(",", "", regex=False), errors="coerce"
)
df_pib = df_pib.dropna(subset=[valor_col])
df_pib = df_pib.sort_values(fecha_col)

# 🔢 Calcular variación anual (4 trimestres)
df_pib["variacion_anual_%"] = df_pib[valor_col].pct_change(4) * 100
variacion_promedio = df_pib["variacion_anual_%"].mean()

print(f"✅ Variación anual promedio del PIB (real): {variacion_promedio:.2f}%")

# Guardar en KPI JSON
Path("data/processed").mkdir(parents=True, exist_ok=True)
kpi_path = Path("data/processed/kpis_macro.json")

macro_kpis = {}
if kpi_path.exists():
    with open(kpi_path, "r", encoding="utf-8") as f:
        macro_kpis = json.load(f)

macro_kpis["variacion_pib_anual_%"] = round(float(variacion_promedio), 2)

with open(kpi_path, "w", encoding="utf-8") as f:
    json.dump(macro_kpis, f, indent=4, ensure_ascii=False)

print(f"💾 KPI actualizado en {kpi_path}")
print("🎯 Proceso completado.")
