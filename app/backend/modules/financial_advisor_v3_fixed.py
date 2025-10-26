# modules/financial_advisor_v3_fixed.py
"""
Sistema de Análisis Financiero CORREGIDO v3.0
Analiza CORRECTAMENTE los datos individuales, no suma todo
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PERSONAL_DATA = os.path.join(BASE_DIR, "data", "internos", "finanzas_personales_limpio.csv")
EMPRESA_DATA = os.path.join(BASE_DIR, "data", "internos", "finanzas_empresa_limpio.csv")

class FinancialAdvisorV3:
    """Asesor financiero CORREGIDO - analiza datos individuales correctamente"""
    
    BENCHMARKS = {
        'pyme': {'margen_min': 5, 'margen_max': 20, 'margen_promedio': 12},
        'mediana': {'margen_min': 8, 'margen_max': 25, 'margen_promedio': 15},
        'grande': {'margen_min': 10, 'margen_max': 30, 'margen_promedio': 18},
        'mercado': {
            'inflacion_anual': 4.5,
            'tasa_referencia': 10.75,
            'cetes_28d': 10.5,
            'tipo_cambio': 17.2
        }
    }
    
    def __init__(self):
        self.personal_df = None
        self.empresa_df = None
        self.usuario_actual = None
        self.empresa_actual = None
        self.load_data()
    

    
    def load_data(self):
        """Cargar datasets"""
        try:
            # --- Cargar datos empresariales ---
            if os.path.exists(EMPRESA_DATA):
                self.empresa_df = pd.read_csv(EMPRESA_DATA)
                self.empresa_df['fecha'] = pd.to_datetime(self.empresa_df['fecha'])
            else:
                print(f"[FinAdvisor] ⚠️ No se encontró archivo EMPRESA_DATA en {EMPRESA_DATA}")
                self.empresa_df = pd.DataFrame()

            # --- Cargar datos personales ---
            if os.path.exists(PERSONAL_DATA):
                self.personal_df = pd.read_csv(PERSONAL_DATA)
                self.personal_df['fecha'] = pd.to_datetime(self.personal_df['fecha'])
            else:
                print(f"[FinAdvisor] ⚠️ No se encontró archivo PERSONAL_DATA en {PERSONAL_DATA}")
                self.personal_df = pd.DataFrame()

            # --- Asignar empresa y usuario por defecto ---
            if len(self.empresa_df) > 0:
                self.empresa_actual = self.empresa_df['empresa_id'].value_counts().index[0]
            if len(self.personal_df) > 0:
                self.usuario_actual = self.personal_df['id_usuario'].value_counts().index[0]

            print("[FinAdvisor] ✅ Datos cargados correctamente")
            print(f"   📊 Empresas disponibles: {self.empresa_df['empresa_id'].nunique()}")
            print(f"   👤 Usuarios disponibles: {self.personal_df['id_usuario'].nunique()}")
            print(f"   🎯 Empresa actual: {self.empresa_actual}")
            print(f"   🎯 Usuario actual: {self.usuario_actual}")

        except Exception as e:
            print(f"[FinAdvisor] ❌ Error al cargar datos: {e}")

    
    def set_empresa(self, empresa_id):
        """Cambiar empresa a analizar"""
        if empresa_id in self.empresa_df['empresa_id'].values:
            self.empresa_actual = empresa_id
            print(f"[FinAdvisor] Cambiado a empresa: {empresa_id}")
            return True
        return False
    
    def set_usuario(self, usuario_id):
        """Cambiar usuario a analizar"""
        if usuario_id in self.personal_df['id_usuario'].values:
            self.usuario_actual = usuario_id
            print(f"[FinAdvisor] Cambiado a usuario: {usuario_id}")
            return True
        return False
    
    def listar_empresas(self):
        """Listar todas las empresas disponibles"""
        empresas = []
        for empresa_id in self.empresa_df['empresa_id'].unique():
            df = self.empresa_df[self.empresa_df['empresa_id'] == empresa_id]
            registros = len(df)
            ingresos = df[df['tipo'] == 'ingreso']['monto'].sum()
            empresas.append({
                'id': empresa_id,
                'registros': registros,
                'ingresos_totales': float(ingresos)
            })
        return sorted(empresas, key=lambda x: x['ingresos_totales'], reverse=True)
    
    def analyze_empresa(self, empresa_id=None):
        """Analiza UNA empresa específica correctamente"""
        
        # Usar empresa especificada o la actual
        if empresa_id is None:
            empresa_id = self.empresa_actual
        
        if empresa_id is None:
            return None
        
        # Filtrar SOLO esta empresa
        df = self.empresa_df[self.empresa_df['empresa_id'] == empresa_id].copy()
        
        if len(df) == 0:
            return None
        
        print(f"\n[Análisis] Empresa {empresa_id}")
        print(f"   Registros totales: {len(df)}")
        
        # Últimos 12 meses REALES (no simular fechas futuras)
        fecha_actual = df['fecha'].max()  # Última fecha real en datos
        fecha_inicio = fecha_actual - timedelta(days=365)
        
        df_12m = df[df['fecha'] >= fecha_inicio].copy()
        print(f"   Período: {fecha_inicio.date()} a {fecha_actual.date()}")
        print(f"   Registros en período: {len(df_12m)}")
        
        # Calcular métricas
        ingresos = df_12m[df_12m['tipo'] == 'ingreso']['monto'].sum()
        gastos = df_12m[df_12m['tipo'] == 'gasto']['monto'].sum()
        utilidad = ingresos - gastos
        margen = (utilidad / ingresos * 100) if ingresos > 0 else 0
        
        print(f"   Ingresos 12m: ${ingresos:,.0f}")
        print(f"   Gastos 12m: ${gastos:,.0f}")
        print(f"   Margen: {margen:.1f}%")
        
        # Gastos por categoría
        gastos_cat = df_12m[df_12m['tipo'] == 'gasto'].groupby('categoria')['monto'].sum()
        
        # Crecimiento trimestral (últimos 3 meses vs 3 anteriores)
        fecha_3m = fecha_actual - timedelta(days=90)
        fecha_6m = fecha_actual - timedelta(days=180)
        
        ing_3m = df[(df['fecha'] >= fecha_3m) & (df['tipo'] == 'ingreso')]['monto'].sum()
        ing_6m = df[(df['fecha'] >= fecha_6m) & (df['fecha'] < fecha_3m) & (df['tipo'] == 'ingreso')]['monto'].sum()
        
        if ing_6m > 0:
            crecimiento = ((ing_3m - ing_6m) / ing_6m * 100)
        else:
            crecimiento = 0
        
        print(f"   Crecimiento 3m: {crecimiento:.1f}%")
        
        # Clasificar tamaño
        if ingresos < 50_000_000:
            tamano = 'pyme'
        elif ingresos < 500_000_000:
            tamano = 'mediana'
        else:
            tamano = 'grande'
        
        benchmark = self.BENCHMARKS[tamano]
        
        # Calcular estado
        estado = self._calcular_estado_empresa(margen, crecimiento, utilidad, ingresos, benchmark)
        
        return {
            'empresa_id': empresa_id,
            'tamano': tamano,
            'periodo_analisis': {
                'inicio': fecha_inicio.strftime('%Y-%m-%d'),
                'fin': fecha_actual.strftime('%Y-%m-%d'),
                'dias': (fecha_actual - fecha_inicio).days
            },
            'metricas': {
                'ingresos_12m': float(ingresos),
                'gastos_12m': float(gastos),
                'utilidad_12m': float(utilidad),
                'margen_utilidad': float(margen),
                'crecimiento_trimestral': float(crecimiento)
            },
            'gastos_por_categoria': {k: float(v) for k, v in gastos_cat.to_dict().items()},
            'benchmark': {
                'margen_promedio': benchmark['margen_promedio'],
                'margen_min': benchmark['margen_min'],
                'margen_max': benchmark['margen_max']
            },
            'estado': estado['categoria'],
            'score': estado['score'],
            'descripcion': estado['descripcion'],
            'alertas': estado['alertas'],
            'recomendaciones': estado['recomendaciones']
        }
    
    def _calcular_estado_empresa(self, margen, crecimiento, utilidad, ingresos, benchmark):
        """Calcula estado con criterios realistas"""
        score = 0
        alertas = []
        recomendaciones = []
        
        # 1. Evaluar margen (40 puntos)
        if margen >= benchmark['margen_max']:
            score += 40
            if margen > 35:
                alertas.append(f"Margen excepcionalmente alto ({margen:.1f}%). Verifica que los datos sean correctos.")
        elif margen >= benchmark['margen_promedio']:
            score += 30
        elif margen >= benchmark['margen_min']:
            score += 20
        elif margen >= 0:
            score += 10
            alertas.append(f"Margen bajo ({margen:.1f}%). Por debajo del mínimo recomendado ({benchmark['margen_min']}%).")
            recomendaciones.append("Reducir gastos operativos o aumentar precios")
        else:
            alertas.append(f"CRÍTICO: Operando en pérdidas (margen {margen:.1f}%)")
            recomendaciones.append("Reestructuración urgente necesaria")
        
        # 2. Evaluar crecimiento (30 puntos)
        if crecimiento >= 15:
            score += 30
        elif crecimiento >= 5:
            score += 20
        elif crecimiento >= 0:
            score += 10
        elif crecimiento >= -10:
            score += 5
            alertas.append(f"Decrecimiento moderado ({crecimiento:.1f}%)")
            recomendaciones.append("Analizar causas del decrecimiento")
        else:
            alertas.append(f"Decrecimiento severo ({crecimiento:.1f}%)")
            recomendaciones.append("Plan de recuperación urgente")
        
        # 3. Utilidad absoluta (20 puntos)
        if utilidad > ingresos * 0.15:
            score += 20
        elif utilidad > ingresos * 0.10:
            score += 15
        elif utilidad > ingresos * 0.05:
            score += 10
        elif utilidad > 0:
            score += 5
        
        # 4. Coherencia (10 puntos)
        if margen > 0 and crecimiento > 0:
            score += 10
        elif margen < 0 and crecimiento < 0:
            score += 5
            alertas.append("Doble problema: pérdidas y decrecimiento")
        elif margen > 30 and crecimiento < -15:
            alertas.append("Incoherencia: Alto margen pero fuerte decrecimiento. Revisar datos.")
        
        # Determinar categoría
        if score >= 70:
            categoria = 'EXCELENTE'
            descripcion = f'Desempeño sobresaliente. Margen de {margen:.1f}% supera el promedio ({benchmark["margen_promedio"]}%).'
        elif score >= 50:
            categoria = 'BUENO'
            descripcion = f'Buen desempeño. Margen de {margen:.1f}% dentro de rangos saludables.'
        elif score >= 30:
            categoria = 'REGULAR'
            descripcion = f'Requiere optimización. Margen de {margen:.1f}%.'
        else:
            categoria = 'CRÍTICO'
            descripcion = 'Situación crítica. Acción inmediata requerida.'
        
        return {
            'categoria': categoria,
            'score': score,
            'descripcion': descripcion,
            'alertas': alertas,
            'recomendaciones': recomendaciones
        }
    
    def analyze_personal(self, usuario_id=None):
        """Analiza finanzas personales de UN usuario"""
        
        if usuario_id is None:
            usuario_id = self.usuario_actual
        
        if usuario_id is None:
            return None
        
        df = self.personal_df[self.personal_df['id_usuario'] == usuario_id].copy()
        
        if len(df) == 0:
            return None
        
        # Últimos 12 meses
        fecha_actual = df['fecha'].max()
        fecha_inicio = fecha_actual - timedelta(days=365)
        df_12m = df[df['fecha'] >= fecha_inicio]
        
        ingresos = df_12m[df_12m['tipo'] == 'ingreso']['monto'].sum()
        gastos = df_12m[df_12m['tipo'] == 'gasto']['monto'].sum()
        ahorro = ingresos - gastos
        tasa_ahorro = (ahorro / ingresos * 100) if ingresos > 0 else 0
        
        gastos_cat = df_12m[df_12m['tipo'] == 'gasto'].groupby('categoria')['monto'].sum()
        
        # Gastos discrecionales
        discrecionales = ['Entretenimiento', 'Restaurantes']
        gasto_disc = sum([gastos_cat.get(cat, 0) for cat in discrecionales])
        pct_disc = (gasto_disc / ingresos * 100) if ingresos > 0 else 0
        
        estado = self._calcular_estado_personal(tasa_ahorro, pct_disc, ingresos)
        
        return {
            'usuario_id': usuario_id,
            'periodo': {
                'inicio': fecha_inicio.strftime('%Y-%m-%d'),
                'fin': fecha_actual.strftime('%Y-%m-%d')
            },
            'metricas': {
                'ingresos_12m': float(ingresos),
                'gastos_12m': float(gastos),
                'ahorro_12m': float(ahorro),
                'tasa_ahorro': float(tasa_ahorro),
                'ingresos_mensuales': float(ingresos / 12),
                'gastos_mensuales': float(gastos / 12),
                'ahorro_mensual': float(ahorro / 12)
            },
            'gastos_por_categoria': {k: float(v) for k, v in gastos_cat.to_dict().items()},
            'gastos_discrecionales_pct': float(pct_disc),
            'estado': estado['categoria'],
            'score': estado['score'],
            'descripcion': estado['descripcion'],
            'alertas': estado['alertas'],
            'recomendaciones': estado['recomendaciones']
        }
    
    def _calcular_estado_personal(self, tasa_ahorro, pct_disc, ingresos):
        """Calcula estado personal"""
        score = 0
        alertas = []
        recomendaciones = []
        
        # Tasa de ahorro (40 puntos)
        if tasa_ahorro >= 25:
            score += 40
        elif tasa_ahorro >= 15:
            score += 30
        elif tasa_ahorro >= 5:
            score += 20
        elif tasa_ahorro >= 0:
            score += 10
            alertas.append(f"Tasa de ahorro baja ({tasa_ahorro:.1f}%)")
            recomendaciones.append("Aumentar ahorro a mínimo 10-15%")
        else:
            alertas.append("CRÍTICO: Gastando más de lo que ganas")
            recomendaciones.append("Reducir gastos urgentemente")
        
        # Gastos discrecionales (30 puntos)
        if pct_disc <= 10:
            score += 30
        elif pct_disc <= 20:
            score += 20
        elif pct_disc <= 30:
            score += 10
            alertas.append(f"Gastos discrecionales altos ({pct_disc:.1f}%)")
        else:
            alertas.append(f"Gastos discrecionales excesivos ({pct_disc:.1f}%)")
            recomendaciones.append("Reducir entretenimiento y restaurantes")
        
        # Nivel de ingresos (30 puntos)
        ing_mensual = ingresos / 12
        if ing_mensual >= 50000:
            score += 30
        elif ing_mensual >= 30000:
            score += 20
        elif ing_mensual >= 15000:
            score += 10
        else:
            recomendaciones.append("Buscar aumentar ingresos")
        
        # Categoría
        if score >= 70:
            categoria = 'EXCELENTE'
            descripcion = f'Finanzas personales excelentes. Tasa de ahorro: {tasa_ahorro:.1f}%'
        elif score >= 50:
            categoria = 'BUENO'
            descripcion = f'Buena salud financiera. Tasa de ahorro: {tasa_ahorro:.1f}%'
        elif score >= 30:
            categoria = 'REGULAR'
            descripcion = f'Finanzas requieren atención. Tasa de ahorro: {tasa_ahorro:.1f}%'
        else:
            categoria = 'CRÍTICO'
            descripcion = 'Situación financiera crítica'
        
        return {
            'categoria': categoria,
            'score': score,
            'descripcion': descripcion,
            'alertas': alertas,
            'recomendaciones': recomendaciones
        }


# Instancia global
_advisor_v3_instance = None

def get_advisor():
    """Obtener instancia del asesor V3"""
    global _advisor_v3_instance
    if _advisor_v3_instance is None:
        _advisor_v3_instance = FinancialAdvisorV3()
    return _advisor_v3_instance
