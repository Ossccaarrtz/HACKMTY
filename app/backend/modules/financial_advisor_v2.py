# modules/financial_advisor_v2.py
"""
Sistema de Análisis Financiero REALISTA v2.0
Con simulador de inversiones avanzado
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Rutas a los datasets
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PERSONAL_DATA = os.path.join(BASE_DIR, "data", "internos", "finanzas_personales_limpio.csv")
EMPRESA_DATA = os.path.join(BASE_DIR, "data", "internos", "finanzas_empresa_limpio.csv")

class FinancialAdvisorV2:
    """Asesor financiero con análisis realista y simulador avanzado"""
    
    # Benchmarks realistas para México (2025)
    BENCHMARKS = {
        'pyme': {
            'margen_min': 5, 'margen_max': 20, 'margen_avg': 12,
            'crecimiento_bueno': 10, 'crecimiento_excelente': 20,
            'ingresos_min': 500_000, 'ingresos_max': 50_000_000
        },
        'mediana': {
            'margen_min': 8, 'margen_max': 25, 'margen_avg': 15,
            'crecimiento_bueno': 8, 'crecimiento_excelente': 15,
            'ingresos_min': 50_000_000, 'ingresos_max': 500_000_000
        },
        'grande': {
            'margen_min': 10, 'margen_max': 30, 'margen_avg': 18,
            'crecimiento_bueno': 5, 'crecimiento_excelente': 12,
            'ingresos_min': 500_000_000, 'ingresos_max': float('inf')
        },
        'personal': {
            'ahorro_minimo': 5, 'ahorro_bueno': 15, 'ahorro_excelente': 25,
            'gastos_discrecionales_max': 20,  # % de ingresos
            'fondo_emergencia_meses': 6
        },
        'mercado_mexico': {
            'inflacion_anual': 4.5,  # % promedio 2025
            'tasa_referencia': 10.75,  # Banxico
            'cetes_28d': 10.5,
            'cetes_91d': 10.8,
            'fibras_rendimiento': 8.5,
            'bolsa_rendimiento_historico': 12.0,
            'sp500_rendimiento_historico': 10.5,
            'tipo_cambio': 17.2,
            'isr_promedio': 30,  # %
            'imss_patron': 5.15  # % sobre nómina
        }
    }
    
    def __init__(self):
        self.personal_df = None
        self.empresa_df = None
        self.load_data()
    
    def load_data(self):
        """Cargar y validar datasets"""
        try:
            self.personal_df = pd.read_csv(PERSONAL_DATA)
            self.personal_df['fecha'] = pd.to_datetime(self.personal_df['fecha'])
            
            self.empresa_df = pd.read_csv(EMPRESA_DATA)
            self.empresa_df['fecha'] = pd.to_datetime(self.empresa_df['fecha'])
            
            print("[FinAdvisor] ✅ Datos cargados y validados")
            print(f"   - Empresas únicas: {self.empresa_df['empresa_id'].nunique()}")
            print(f"   - Usuarios únicos: {self.personal_df['id_usuario'].nunique()}")
            
        except Exception as e:
            print(f"[FinAdvisor] ❌ Error cargando datos: {e}")
    
    def _clasificar_empresa_por_tamano(self, ingresos_anuales):
        """Clasifica empresa según ingresos"""
        if ingresos_anuales < self.BENCHMARKS['pyme']['ingresos_max']:
            return 'pyme'
        elif ingresos_anuales < self.BENCHMARKS['mediana']['ingresos_max']:
            return 'mediana'
        else:
            return 'grande'
    
    def _validar_metricas_empresa(self, metricas):
        """Valida que las métricas sean realistas"""
        problemas = []
        
        # Validar margen de utilidad
        if metricas['margen_utilidad'] > 50:
            problemas.append(f"Margen del {metricas['margen_utilidad']:.1f}% es irrealmente alto (máx esperado: 30%)")
        elif metricas['margen_utilidad'] < -50:
            problemas.append(f"Pérdidas del {abs(metricas['margen_utilidad']):.1f}% son insostenibles")
        
        # Validar coherencia crecimiento-estado
        if metricas['crecimiento_trimestral'] < -15 and metricas['margen_utilidad'] > 30:
            problemas.append("Incoherencia: alto margen pero decrecimiento fuerte")
        
        # Validar utilidad vs ingresos
        if abs(metricas['utilidad_neta']) > metricas['ingresos_anuales']:
            problemas.append("Error: utilidad mayor a ingresos totales")
        
        return problemas
    
    # ========================================
    # ANÁLISIS EMPRESARIAL REALISTA
    # ========================================
    
    def analyze_empresa(self, empresa_id=None):
        """Análisis empresarial con validación realista"""
        
        if empresa_id:
            df = self.empresa_df[self.empresa_df['empresa_id'] == empresa_id].copy()
            if len(df) == 0:
                return None
        else:
            # Analizar UNA empresa representativa, no todas juntas
            empresa_ids = self.empresa_df['empresa_id'].unique()
            if len(empresa_ids) > 0:
                # Tomar empresa con más datos
                empresa_counts = self.empresa_df['empresa_id'].value_counts()
                empresa_id = empresa_counts.index[0]
                df = self.empresa_df[self.empresa_df['empresa_id'] == empresa_id].copy()
            else:
                return None
        
        # Últimos 12 meses para análisis anual
        fecha_limite = datetime.now() - timedelta(days=365)
        df_reciente = df[df['fecha'] >= fecha_limite].copy()
        
        if len(df_reciente) == 0:
            # Si no hay datos recientes, usar todo
            df_reciente = df.copy()
        
        # Calcular métricas
        ingresos = df_reciente[df_reciente['tipo'] == 'ingreso']['monto'].sum()
        gastos = df_reciente[df_reciente['tipo'] == 'gasto']['monto'].sum()
        utilidad = ingresos - gastos
        margen = (utilidad / ingresos * 100) if ingresos > 0 else 0
        
        # Desglose de gastos
        gastos_por_cat = df_reciente[df_reciente['tipo'] == 'gasto'].groupby('categoria')['monto'].sum()
        
        # Tendencia trimestral (últimos 3 meses vs previos 3)
        fecha_3m = datetime.now() - timedelta(days=90)
        fecha_6m = datetime.now() - timedelta(days=180)
        
        df_3m = df[(df['fecha'] >= fecha_3m) & (df['tipo'] == 'ingreso')]
        df_6m = df[(df['fecha'] >= fecha_6m) & (df['fecha'] < fecha_3m) & (df['tipo'] == 'ingreso')]
        
        ingresos_3m = df_3m['monto'].sum()
        ingresos_6m = df_6m['monto'].sum()
        
        # Calcular crecimiento
        if ingresos_6m > 0:
            crecimiento = ((ingresos_3m - ingresos_6m) / ingresos_6m * 100)
        else:
            crecimiento = 0 if ingresos_3m == 0 else 100
        
        # Clasificar empresa
        tamano = self._clasificar_empresa_por_tamano(ingresos)
        benchmark = self.BENCHMARKS[tamano]
        
        # Crear análisis
        analisis = {
            'empresa_id': empresa_id,
            'tamano': tamano,
            'ingresos_anuales': float(ingresos),
            'gastos_anuales': float(gastos),
            'utilidad_neta': float(utilidad),
            'margen_utilidad': float(margen),
            'crecimiento_trimestral': float(crecimiento),
            'gastos_por_categoria': {k: float(v) for k, v in gastos_por_cat.to_dict().items()},
            'benchmark_margen': benchmark['margen_avg'],
            'benchmark_crecimiento': benchmark['crecimiento_bueno']
        }
        
        # Validar coherencia
        problemas = self._validar_metricas_empresa(analisis)
        analisis['validacion'] = {
            'es_realista': len(problemas) == 0,
            'problemas': problemas
        }
        
        # Calcular estado REALISTA
        estado = self._calcular_estado_empresa_realista(analisis, benchmark)
        analisis.update(estado)
        
        return analisis
    
    def _calcular_estado_empresa_realista(self, analisis, benchmark):
        """Calcula estado con criterios realistas"""
        score = 0
        alertas = []
        
        margen = analisis['margen_utilidad']
        crecimiento = analisis['crecimiento_trimestral']
        utilidad = analisis['utilidad_neta']
        ingresos = analisis['ingresos_anuales']
        
        # 1. MARGEN DE UTILIDAD (40 puntos) - comparado con benchmark
        if margen >= benchmark['margen_max']:
            score += 40
        elif margen >= benchmark['margen_avg']:
            score += 30
        elif margen >= benchmark['margen_min']:
            score += 20
        elif margen >= 0:
            score += 10
            alertas.append(f"Margen de {margen:.1f}% está por debajo del promedio de la industria ({benchmark['margen_avg']}%)")
        else:
            alertas.append(f"CRÍTICO: Empresa en pérdidas con margen de {margen:.1f}%")
        
        # 2. CRECIMIENTO (30 puntos) - debe ser coherente con margen
        if crecimiento >= benchmark['crecimiento_excelente']:
            score += 30
        elif crecimiento >= benchmark['crecimiento_bueno']:
            score += 20
        elif crecimiento >= 0:
            score += 10
        elif crecimiento >= -10:
            score += 5
            alertas.append(f"Decrecimiento de {crecimiento:.1f}% requiere atención")
        else:
            alertas.append(f"CRÍTICO: Decrecimiento severo de {crecimiento:.1f}%")
        
        # 3. UTILIDAD ABSOLUTA (20 puntos)
        if utilidad > ingresos * 0.15:
            score += 20
        elif utilidad > ingresos * 0.10:
            score += 15
        elif utilidad > ingresos * 0.05:
            score += 10
        elif utilidad > 0:
            score += 5
        else:
            alertas.append("Empresa operando en pérdidas")
        
        # 4. COHERENCIA (10 puntos) - validar lógica
        if margen > 30 and crecimiento < -15:
            score -= 10  # Penalizar incoherencias
            alertas.append("Incoherencia detectada: alto margen pero fuerte decrecimiento")
        elif margen < 0 and crecimiento > 20:
            score -= 10
            alertas.append("Incoherencia detectada: pérdidas pero alto crecimiento (posible inversión)")
        else:
            score += 10
        
        # Determinar categoría CON COHERENCIA
        if score >= 70 and crecimiento >= 0 and margen >= benchmark['margen_avg']:
            categoria = 'EXCELENTE'
            descripcion = f'Empresa {analisis["tamano"]} con desempeño sobresaliente. Margen de {margen:.1f}% supera el promedio sectorial ({benchmark["margen_avg"]}%).'
        elif score >= 50 and margen >= benchmark['margen_min']:
            categoria = 'BUENO'
            descripcion = f'Empresa {analisis["tamano"]} con buen desempeño. Margen de {margen:.1f}% dentro de rangos saludables.'
        elif score >= 30:
            categoria = 'REGULAR'
            descripcion = f'Empresa {analisis["tamano"]} requiere optimización. Margen de {margen:.1f}% {"por debajo" if margen < benchmark["margen_avg"] else "aceptable pero"} del promedio sectorial.'
        else:
            categoria = 'CRÍTICO'
            descripcion = f'Empresa {analisis["tamano"]} en situación crítica. Se requiere acción inmediata.'
        
        return {
            'estado': categoria,
            'score': min(100, max(0, score)),  # Limitar entre 0-100
            'descripcion': descripcion,
            'alertas': alertas
        }
    
    # ========================================
    # ANÁLISIS PERSONAL REALISTA
    # ========================================
    
    def analyze_personal(self, usuario_id=None):
        """Análisis de finanzas personales con criterios realistas"""
        
        if usuario_id:
            df = self.personal_df[self.personal_df['id_usuario'] == usuario_id].copy()
        else:
            # Analizar UN usuario representativo
            usuario_ids = self.personal_df['id_usuario'].unique()
            if len(usuario_ids) > 0:
                usuario_counts = self.personal_df['id_usuario'].value_counts()
                usuario_id = usuario_counts.index[0]
                df = self.personal_df[self.personal_df['id_usuario'] == usuario_id].copy()
            else:
                return None
        
        if len(df) == 0:
            return None
        
        # Últimos 12 meses
        fecha_limite = datetime.now() - timedelta(days=365)
        df_reciente = df[df['fecha'] >= fecha_limite]
        
        if len(df_reciente) == 0:
            df_reciente = df
        
        # Calcular métricas
        ingresos = df_reciente[df_reciente['tipo'] == 'ingreso']['monto'].sum()
        gastos = df_reciente[df_reciente['tipo'] == 'gasto']['monto'].sum()
        ahorro_total = ingresos - gastos
        tasa_ahorro = (ahorro_total / ingresos * 100) if ingresos > 0 else 0
        
        # Promedios mensuales
        ingresos_mensuales = ingresos / 12
        gastos_mensuales = gastos / 12
        ahorro_mensual = ahorro_total / 12
        
        # Desglose
        gastos_por_cat = df_reciente[df_reciente['tipo'] == 'gasto'].groupby('categoria')['monto'].sum()
        
        # Gastos discrecionales
        categorias_discrecionales = ['Entretenimiento', 'Restaurantes']
        gasto_discrecional = sum([gastos_por_cat.get(cat, 0) for cat in categorias_discrecionales])
        pct_discrecional = (gasto_discrecional / ingresos * 100) if ingresos > 0 else 0
        
        # Fondo de emergencia
        fondo_emergencia_actual = ahorro_total if ahorro_total > 0 else 0
        fondo_emergencia_objetivo = gastos_mensuales * self.BENCHMARKS['personal']['fondo_emergencia_meses']
        pct_fondo = (fondo_emergencia_actual / fondo_emergencia_objetivo * 100) if fondo_emergencia_objetivo > 0 else 0
        
        analisis = {
            'usuario_id': usuario_id,
            'ingresos_anuales': float(ingresos),
            'gastos_anuales': float(gastos),
            'ahorro_total': float(ahorro_total),
            'tasa_ahorro': float(tasa_ahorro),
            'ingresos_mensuales': float(ingresos_mensuales),
            'gastos_mensuales': float(gastos_mensuales),
            'ahorro_mensual': float(ahorro_mensual),
            'gastos_por_categoria': {k: float(v) for k, v in gastos_por_cat.to_dict().items()},
            'pct_gastos_discrecionales': float(pct_discrecional),
            'fondo_emergencia_actual': float(fondo_emergencia_actual),
            'fondo_emergencia_objetivo': float(fondo_emergencia_objetivo),
            'pct_fondo_emergencia': float(pct_fondo)
        }
        
        # Calcular estado
        estado = self._calcular_estado_personal_realista(analisis)
        analisis.update(estado)
        
        return analisis
    
    def _calcular_estado_personal_realista(self, analisis):
        """Calcula estado financiero personal con criterios realistas"""
        score = 0
        alertas = []
        
        tasa_ahorro = analisis['tasa_ahorro']
        pct_discrecional = analisis['pct_gastos_discrecionales']
        pct_fondo = analisis['pct_fondo_emergencia']
        
        bench = self.BENCHMARKS['personal']
        
        # 1. TASA DE AHORRO (40 puntos)
        if tasa_ahorro >= bench['ahorro_excelente']:
            score += 40
        elif tasa_ahorro >= bench['ahorro_bueno']:
            score += 30
        elif tasa_ahorro >= bench['ahorro_minimo']:
            score += 20
        elif tasa_ahorro >= 0:
            score += 10
            alertas.append(f"Tasa de ahorro de {tasa_ahorro:.1f}% está por debajo del mínimo recomendado ({bench['ahorro_minimo']}%)")
        else:
            alertas.append(f"CRÍTICO: Estás gastando más de lo que ganas ({tasa_ahorro:.1f}%)")
        
        # 2. FONDO DE EMERGENCIA (30 puntos)
        if pct_fondo >= 100:
            score += 30
        elif pct_fondo >= 50:
            score += 20
        elif pct_fondo >= 25:
            score += 10
        else:
            alertas.append(f"Fondo de emergencia insuficiente: solo {pct_fondo:.0f}% del objetivo ({bench['fondo_emergencia_meses']} meses de gastos)")
        
        # 3. CONTROL DE GASTOS DISCRECIONALES (20 puntos)
        if pct_discrecional <= 10:
            score += 20
        elif pct_discrecional <= bench['gastos_discrecionales_max']:
            score += 15
        elif pct_discrecional <= 30:
            score += 10
            alertas.append(f"Gastos discrecionales altos: {pct_discrecional:.1f}% de ingresos (recomendado: <{bench['gastos_discrecionales_max']}%)")
        else:
            alertas.append(f"ALERTA: Gastos discrecionales excesivos ({pct_discrecional:.1f}% de ingresos)")
        
        # 4. DIVERSIFICACIÓN (10 puntos)
        tiene_ahorro_formal = 'Ahorro' in analisis['gastos_por_categoria']
        tiene_educacion = 'Educación' in analisis['gastos_por_categoria']
        
        if tiene_ahorro_formal and tiene_educacion:
            score += 10
        elif tiene_ahorro_formal or tiene_educacion:
            score += 5
        
        # Determinar categoría
        if score >= 70:
            categoria = 'EXCELENTE'
            descripcion = f'Finanzas personales en excelente estado con tasa de ahorro del {tasa_ahorro:.1f}%.'
        elif score >= 50:
            categoria = 'BUENO'
            descripcion = f'Buena salud financiera con tasa de ahorro del {tasa_ahorro:.1f}%.'
        elif score >= 30:
            categoria = 'REGULAR'
            descripcion = f'Finanzas requieren atención. Tasa de ahorro: {tasa_ahorro:.1f}%.'
        else:
            categoria = 'CRÍTICO'
            descripcion = 'Situación financiera crítica. Se requiere acción urgente.'
        
        return {
            'estado': categoria,
            'score': score,
            'descripcion': descripcion,
            'alertas': alertas
        }
    
    # ========================================
    # SIMULADOR DE INVERSIONES ÉPICO
    # ========================================
    
    def simular_inversion(self, monto_inicial, aportacion_mensual, plazo_meses, tipo_inversion, considera_inflacion=True):
        """
        Simulador avanzado de inversiones
        
        Args:
            monto_inicial: Capital inicial en MXN
            aportacion_mensual: Aportación mensual en MXN
            plazo_meses: Plazo en meses
            tipo_inversion: 'conservador', 'moderado', 'agresivo', 'cetes', 'fibras', 'sp500'
            considera_inflacion: Si ajustar por inflación
        
        Returns:
            dict con resultados detallados
        """
        
        mercado = self.BENCHMARKS['mercado_mexico']
        
        # Definir portafolios
        portafolios = {
            'conservador': {
                'cetes_28d': 0.60,
                'cetes_91d': 0.30,
                'fibras': 0.10,
                'rendimiento_esperado': 9.5,
                'volatilidad': 0.02
            },
            'moderado': {
                'cetes_28d': 0.30,
                'fibras': 0.40,
                'bolsa_mexico': 0.20,
                'sp500': 0.10,
                'rendimiento_esperado': 10.8,
                'volatilidad': 0.08
            },
            'agresivo': {
                'sp500': 0.50,
                'bolsa_mexico': 0.30,
                'fibras': 0.15,
                'cetes_91d': 0.05,
                'rendimiento_esperado': 11.5,
                'volatilidad': 0.15
            },
            'cetes': {
                'cetes_28d': 1.0,
                'rendimiento_esperado': mercado['cetes_28d'],
                'volatilidad': 0.01
            },
            'fibras': {
                'fibras': 1.0,
                'rendimiento_esperado': mercado['fibras_rendimiento'],
                'volatilidad': 0.05
            },
            'sp500': {
                'sp500': 1.0,
                'rendimiento_esperado': mercado['sp500_rendimiento_historico'],
                'volatilidad': 0.18
            }
        }
        
        config = portafolios.get(tipo_inversion, portafolios['moderado'])
        
        # Simulación mensual
        rendimiento_mensual = (1 + config['rendimiento_esperado']/100)**(1/12) - 1
        inflacion_mensual = (1 + mercado['inflacion_anual']/100)**(1/12) - 1
        
        resultados_mes = []
        saldo = monto_inicial
        total_aportado = monto_inicial
        
        for mes in range(1, plazo_meses + 1):
            # Rendimiento con variación estocástica
            variacion = np.random.normal(0, config['volatilidad'])
            rendimiento_mes = rendimiento_mensual + variacion
            
            # Aplicar rendimiento
            rendimiento_pesos = saldo * rendimiento_mes
            saldo += rendimiento_pesos
            
            # Aportación mensual
            if mes < plazo_meses:  # No aportar en el último mes
                saldo += aportacion_mensual
                total_aportado += aportacion_mensual
            
            # Valor real (ajustado por inflación)
            if considera_inflacion:
                factor_inflacion = (1 + inflacion_mensual) ** mes
                saldo_real = saldo / factor_inflacion
            else:
                saldo_real = saldo
            
            resultados_mes.append({
                'mes': mes,
                'saldo_nominal': saldo,
                'saldo_real': saldo_real,
                'rendimiento_mes': rendimiento_pesos,
                'total_aportado': total_aportado
            })
        
        # Resultados finales
        resultado_final = resultados_mes[-1]
        ganancia_nominal = resultado_final['saldo_nominal'] - total_aportado
        ganancia_real = resultado_final['saldo_real'] - total_aportado
        
        roi_nominal = (ganancia_nominal / total_aportado * 100) if total_aportado > 0 else 0
        roi_real = (ganancia_real / total_aportado * 100) if total_aportado > 0 else 0
        
        # Calcular rendimiento anualizado
        rendimiento_anualizado = (((resultado_final['saldo_nominal'] / monto_inicial) ** (12/plazo_meses)) - 1) * 100
        
        return {
            'configuracion': {
                'tipo': tipo_inversion,
                'monto_inicial': monto_inicial,
                'aportacion_mensual': aportacion_mensual,
                'plazo_meses': plazo_meses,
                'plazo_anos': plazo_meses / 12,
                'portafolio': {k: v for k, v in config.items() if k not in ['rendimiento_esperado', 'volatilidad']},
                'rendimiento_esperado_anual': config['rendimiento_esperado'],
                'volatilidad': config['volatilidad']
            },
            'resultados': {
                'total_aportado': total_aportado,
                'saldo_final_nominal': resultado_final['saldo_nominal'],
                'saldo_final_real': resultado_final['saldo_real'] if considera_inflacion else resultado_final['saldo_nominal'],
                'ganancia_nominal': ganancia_nominal,
                'ganancia_real': ganancia_real if considera_inflacion else ganancia_nominal,
                'roi_nominal': roi_nominal,
                'roi_real': roi_real if considera_inflacion else roi_nominal,
                'rendimiento_anualizado': rendimiento_anualizado
            },
            'desglose_mensual': resultados_mes[-12:],  # Últimos 12 meses
            'analisis': self._analizar_simulacion(resultado_final, total_aportado, config, plazo_meses)
        }
    
    def _analizar_simulacion(self, resultado_final, total_aportado, config, plazo_meses):
        """Analiza resultados de la simulación y da recomendaciones"""
        
        ganancia = resultado_final['saldo_nominal'] - total_aportado
        roi = (ganancia / total_aportado * 100) if total_aportado > 0 else 0
        
        analisis = {
            'viabilidad': 'ALTA',
            'riesgo': 'BAJO',
            'recomendaciones': []
        }
        
        # Evaluar viabilidad
        if roi < 5:
            analisis['viabilidad'] = 'BAJA'
            analisis['recomendaciones'].append("Rendimiento proyectado por debajo de la inflación. Considera opciones más rentables.")
        elif roi < 10:
            analisis['viabilidad'] = 'MEDIA'
            analisis['recomendaciones'].append("Rendimiento moderado. Considera diversificar para mejorar retorno.")
        else:
            analisis['viabilidad'] = 'ALTA'
            analisis['recomendaciones'].append("Proyección de rendimiento sólida. Mantén la disciplina de ahorro.")
        
        # Evaluar riesgo
        if config['volatilidad'] < 0.05:
            analisis['riesgo'] = 'BAJO'
        elif config['volatilidad'] < 0.12:
            analisis['riesgo'] = 'MEDIO'
        else:
            analisis['riesgo'] = 'ALTO'
            analisis['recomendaciones'].append("Alta volatilidad. Solo recomendado si tienes horizonte de largo plazo (5+ años).")
        
        # Recomendaciones según plazo
        if plazo_meses < 12:
            analisis['recomendaciones'].append("Plazo corto: Prefiere instrumentos de bajo riesgo como CETES.")
        elif plazo_meses < 36:
            analisis['recomendaciones'].append("Plazo medio: Considera portafolio balanceado entre renta fija y variable.")
        else:
            analisis['recomendaciones'].append("Plazo largo: Puedes tomar más riesgo para mayor rendimiento potencial.")
        
        return analisis
    
    def comparar_inversiones(self, monto_inicial, aportacion_mensual, plazo_meses):
        """Compara múltiples opciones de inversión"""
        
        opciones = ['conservador', 'moderado', 'agresivo', 'cetes', 'fibras', 'sp500']
        comparativa = []
        
        for opcion in opciones:
            resultado = self.simular_inversion(
                monto_inicial=monto_inicial,
                aportacion_mensual=aportacion_mensual,
                plazo_meses=plazo_meses,
                tipo_inversion=opcion,
                considera_inflacion=True
            )
            
            comparativa.append({
                'tipo': opcion,
                'saldo_final': resultado['resultados']['saldo_final_real'],
                'ganancia': resultado['resultados']['ganancia_real'],
                'roi': resultado['resultados']['roi_real'],
                'rendimiento_anualizado': resultado['resultados']['rendimiento_anualizado'],
                'riesgo': resultado['analisis']['riesgo'],
                'viabilidad': resultado['analisis']['viabilidad']
            })
        
        # Ordenar por ROI
        comparativa.sort(key=lambda x: x['roi'], reverse=True)
        
        return {
            'parametros': {
                'monto_inicial': monto_inicial,
                'aportacion_mensual': aportacion_mensual,
                'plazo_meses': plazo_meses
            },
            'opciones': comparativa,
            'recomendacion': self._recomendar_mejor_opcion(comparativa, plazo_meses)
        }
    
    def _recomendar_mejor_opcion(self, comparativa, plazo_meses):
        """Recomienda la mejor opción según perfil de riesgo y plazo"""
        
        if plazo_meses < 12:
            # Plazo corto: priorizar seguridad
            mejor = [x for x in comparativa if x['riesgo'] == 'BAJO']
            if mejor:
                return {
                    'opcion': mejor[0]['tipo'],
                    'razon': 'Plazo corto requiere bajo riesgo. Esta opción protege tu capital.',
                    'alternativa': comparativa[0]['tipo'] if comparativa[0]['riesgo'] != 'BAJO' else None
                }
        elif plazo_meses < 36:
            # Plazo medio: balancear riesgo-retorno
            mejor = [x for x in comparativa if x['riesgo'] in ['BAJO', 'MEDIO']]
            if mejor:
                mejor.sort(key=lambda x: x['roi'], reverse=True)
                return {
                    'opcion': mejor[0]['tipo'],
                    'razon': 'Plazo medio permite balance entre rendimiento y seguridad.',
                    'alternativa': mejor[1]['tipo'] if len(mejor) > 1 else None
                }
        else:
            # Plazo largo: maximizar rendimiento
            return {
                'opcion': comparativa[0]['tipo'],
                'razon': 'Plazo largo permite aprovechar crecimiento con mayor riesgo.',
                'alternativa': comparativa[1]['tipo']
            }
        
        return {
            'opcion': comparativa[0]['tipo'],
            'razon': 'Mayor rendimiento esperado ajustado por riesgo.',
            'alternativa': comparativa[1]['tipo'] if len(comparativa) > 1 else None
        }


# Instancia global
_advisor_v2_instance = None

def get_advisor():
    """Obtener instancia del asesor financiero V2"""
    global _advisor_v2_instance
    if _advisor_v2_instance is None:
        _advisor_v2_instance = FinancialAdvisorV2()
    return _advisor_v2_instance
