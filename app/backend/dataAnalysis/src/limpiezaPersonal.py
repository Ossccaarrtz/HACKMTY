import pandas as pd

# 1️⃣ Cargar el Excel indicando la codificación correcta
df = pd.read_excel("finanzas_personales.xlsx", engine="openpyxl")

# 2️⃣ Reparar caracteres mal interpretados (mojibake)
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].astype(str).apply(lambda x: x.encode('latin1', errors='ignore').decode('utf-8', errors='ignore'))

# 3️⃣ Guardar el CSV limpio en UTF-8 para que funcione en cualquier sistema
df.to_csv("finanzas_personales_limpio.csv", index=False, encoding="utf-8")

print("✅ CSV limpio creado correctamente.")
