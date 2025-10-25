import pandas as pd
from pathlib import Path
import json

# ======================================================
# 🚀 GENERADOR DE KPIs – FINCORTEX / HACKMTY
# ======================================================
# Crea KPIs para:
#   1️⃣ Empresas
#   2️⃣ Usuarios personales
#   3️⃣ Variables macroeconómicas
# ======================================================

# Crear carpeta destino si no existe
Path("data/processed").mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------
# 🏢 1️⃣ KPIs EMPRESARIALES
# ------------------------------------------------------
try:
    df_emp = pd.read_csv("data/internos/finanzas_empresa_limpio.csv")
    df_emp["fecha"] = pd.to_datetime(df_emp["fecha"], errors="coerce")

    # Flujo neto mensual (ingresos - gastos)
    flujo = (
        df_emp.groupby(["empresa_id", pd.Grouper(key="fecha", freq="M")])
        .apply(
            lambda x: x.loc[x["tipo"] == "ingreso", "monto"].sum()
            - x.loc[x["tipo"] == "gasto", "monto"].sum()
        )
        .reset_index(name="flujo_neto")
    )

    # Margen operativo (%)
    margen = (
        df_emp.groupby("empresa_id")
        .apply(
            lambda x: (
                x.loc[x["tipo"] == "ingreso", "monto"].sum()
                - x.loc[x["tipo"] == "gasto", "monto"].sum()
            )
            / max(x.loc[x["tipo"] == "ingreso", "monto"].sum(), 1)
        )
        .reset_index(name="margen_operativo")
    )

    # Gasto promedio mensual
    gasto_promedio = (
        df_emp[df_emp["tipo"] == "gasto"]
        .groupby("empresa_id")["monto"]
        .mean()
        .reset_index(name="gasto_promedio")
    )

    # Combinar resultados
    emp_kpis = flujo.merge(margen, on="empresa_id", how="left").merge(
        gasto_promedio, on="empresa_id", how="left"
    )

    emp_kpis.to_csv("data/processed/kpis_empresas.csv", index=False, encoding="utf-8")
    print("✅ KPIs empresariales guardados en data/processed/kpis_empresas.csv")

except Exception as e:
    print(f"⚠️ Error generando KPIs empresariales: {e}")

# ------------------------------------------------------
# 👤 2️⃣ KPIs PERSONALES
# ------------------------------------------------------
try:
    df_per = pd.read_csv("data/internos/finanzas_personales_limpio.csv")
    df_per["fecha"] = pd.to_datetime(df_per["fecha"], errors="coerce")

    # Flujo mensual (ingresos - gastos)
    flujo_personal = (
        df_per.groupby(["id_usuario", pd.Grouper(key="fecha", freq="M")])
        .apply(
            lambda x: x.loc[x["tipo"] == "ingreso", "monto"].sum()
            - x.loc[x["tipo"] == "gasto", "monto"].sum()
        )
        .reset_index(name="ahorro_mensual")
    )

    # Tasa de ahorro
    tasa_ahorro = (
        df_per.groupby("id_usuario")
        .apply(
            lambda x: (
                x.loc[x["tipo"] == "ingreso", "monto"].sum()
                - x.loc[x["tipo"] == "gasto", "monto"].sum()
            )
            / max(x.loc[x["tipo"] == "ingreso", "monto"].sum(), 1)
        )
        .reset_index(name="tasa_ahorro")
    )

    # Gasto promedio mensual
    gasto_promedio = (
        df_per[df_per["tipo"] == "gasto"]
        .groupby("id_usuario")["monto"]
        .mean()
        .reset_index(name="gasto_promedio")
    )

    # Combinar
    per_kpis = flujo_personal.merge(tasa_ahorro, on="id_usuario", how="left").merge(
        gasto_promedio, on="id_usuario", how="left"
    )

    per_kpis.to_csv("data/processed/kpis_personales.csv", index=False, encoding="utf-8")
    print("✅ KPIs personales guardados en data/processed/kpis_personales.csv")

except Exception as e:
    print(f"⚠️ Error generando KPIs personales: {e}")

# ------------------------------------------------------
# 🌎 3️⃣ KPIs MACROECONÓMICOS (versión adaptada a tus columnas)
# ------------------------------------------------------
try:
    df_macro = pd.read_csv("data/processed/macro_features.csv")
    df_macro["fecha"] = pd.to_datetime(df_macro["fecha"], errors="coerce")

    # Usamos los nombres reales de tus columnas
    inflacion_col = "inpc_general"
    tasa_col = "tasa_referencia"
    pib_col = "pib_trimestral_desestacionalizado"

    macro_kpis = {
        # Inflación promedio mensual (índice INPC general)
        "inflacion_promedio_mensual": float(df_macro[inflacion_col].pct_change().mean() * 100),

        # Tasa de referencia promedio
        "tasa_referencia_media": float(df_macro[tasa_col].mean()),

        # Variación anual del PIB
        "variacion_pib_anual_%": float(df_macro[pib_col].pct_change(4).mean() * 100)
,
    }

    # Guardar como JSON
    with open("data/processed/kpis_macro.json", "w", encoding="utf-8") as f:
        json.dump(macro_kpis, f, indent=4, ensure_ascii=False)

    print("✅ KPIs macroeconómicos guardados en data/processed/kpis_macro.json")
    print("🌎 Resumen:")
    for k, v in macro_kpis.items():
        print(f"   {k}: {v:.2f}")

except Exception as e:
    print(f"⚠️ Error generando KPIs macroeconómicos: {e}")


print("\n🎯 Proceso completado con éxito.")
