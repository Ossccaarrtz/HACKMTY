# modules/financial_advisor.py
"""
Sistema de Análisis Financiero Inteligente
Analiza finanzas personales y empresariales para dar recomendaciones realistas
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Rutas a los datasets
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PERSONAL_DATA = os.path.join(BASE_DIR, "data", "internos", "finanzas_personales_limpio.csv")
EMPRESA_DATA = os.path.join(BASE_DIR, "data", "internos", "finanzas_empresa_limpio.csv")

class FinancialAdvisor:
    """Asesor financiero inteligente"""
    
    def __init__(self):
        self.personal_df = None
        self.empresa_df = None
        self.load_data()
    
    def load_data(self):
        """Cargar datasets"""
        try:
            self.personal_df = pd.read_csv(PERSONAL_DATA)
            self.personal_df['fecha'] = pd.to_datetime(self.personal_df['fecha'])
            
            self.empresa_df = pd.read_csv(EMPRESA_DATA)
            self.empresa_df['fecha'] = pd.to_datetime(self.empresa_df['fecha'])
            
            print("[FinAdvisor] ✅ Datos cargados correctamente")
        except Exception as e:
            print(f"[FinAdvisor] ❌ Error cargando datos: {e}")
    
    # ========================================
    # ANÁLISIS EMPRESARIAL
    # ========================================
    
    def analyze_empresa(self, empresa_id=None):
        """Analiza el estado financiero de una empresa"""
        
        if empresa_id:
            df = self.empresa_df[self.empresa_df['empresa_id'] == empresa_id].copy()
        else:
            # Si no se especifica, tomar todas las empresas
            df = self.empresa_df.copy()
        
        if len(df) == 0:
            return None
        
        # Últimos 12 meses
        fecha_limite = datetime.now() - timedelta(days=365)
        df_reciente = df[df['fecha'] >= fecha_limite]
        
        # Calcular métricas
        ingresos = df_reciente[df_reciente['tipo'] == 'ingreso']['monto'].sum()
        gastos = df_reciente[df_reciente['tipo'] == 'gasto']['monto'].sum()
        utilidad = ingresos - gastos
        margen = (utilidad / ingresos * 100) if ingresos > 0 else 0
        
        # Desglose de gastos
        gastos_por_cat = df_reciente[df_reciente['tipo'] == 'gasto'].groupby('categoria')['monto'].sum()
        
        # Tendencia (últimos 3 meses vs previos 3)
        fecha_3m = datetime.now() - timedelta(days=90)
        fecha_6m = datetime.now() - timedelta(days=180)
        
        ingresos_recientes = df[(df['fecha'] >= fecha_3m) & (df['tipo'] == 'ingreso')]['monto'].sum()
        ingresos_previos = df[(df['fecha'] >= fecha_6m) & (df['fecha'] < fecha_3m) & (df['tipo'] == 'ingreso')]['monto'].sum()
        
        crecimiento = ((ingresos_recientes - ingresos_previos) / ingresos_previos * 100) if ingresos_previos > 0 else 0
        
        # Determinar estado
        estado = self._calcular_estado_empresa(margen, crecimiento, utilidad)
        
        return {
            'ingresos_anuales': float(ingresos),
            'gastos_anuales': float(gastos),
            'utilidad_neta': float(utilidad),
            'margen_utilidad': float(margen),
            'crecimiento_trimestral': float(crecimiento),
            'gastos_por_categoria': gastos_por_cat.to_dict(),
            'estado': estado['categoria'],
            'score': estado['score'],
            'descripcion': estado['descripcion']
        }
    
    def _calcular_estado_empresa(self, margen, crecimiento, utilidad):
        """Calcula el estado de salud de la empresa"""
        score = 0
        
        # Margen de utilidad (40 puntos máximo)
        if margen >= 20:
            score += 40
        elif margen >= 10:
            score += 30
        elif margen >= 5:
            score += 20
        elif margen >= 0:
            score += 10
        
        # Crecimiento (30 puntos máximo)
        if crecimiento >= 15:
            score += 30
        elif crecimiento >= 5:
            score += 20
        elif crecimiento >= 0:
            score += 10
        elif crecimiento >= -5:
            score += 5
        
        # Utilidad positiva (30 puntos máximo)
        if utilidad > 0:
            score += 30
        elif utilidad > -100000:
            score += 15
        
        # Determinar categoría
        if score >= 70:
            return {
                'categoria': 'EXCELENTE',
                'score': score,
                'descripcion': 'La empresa está en excelente estado financiero'
            }
        elif score >= 50:
            return {
                'categoria': 'BUENO',
                'score': score,
                'descripcion': 'La empresa tiene buen desempeño financiero'
            }
        elif score >= 30:
            return {
                'categoria': 'REGULAR',
                'score': score,
                'descripcion': 'La empresa requiere atención en algunas áreas'
            }
        else:
            return {
                'categoria': 'CRÍTICO',
                'score': score,
                'descripcion': 'La empresa necesita acciones urgentes'
            }
    
    # ========================================
    # ANÁLISIS PERSONAL
    # ========================================
    
    def analyze_personal(self, usuario_id=None):
        """Analiza finanzas personales"""
        
        if usuario_id:
            df = self.personal_df[self.personal_df['id_usuario'] == usuario_id].copy()
        else:
            df = self.personal_df.copy()
        
        if len(df) == 0:
            return None
        
        # Últimos 12 meses
        fecha_limite = datetime.now() - timedelta(days=365)
        df_reciente = df[df['fecha'] >= fecha_limite]
        
        # Calcular métricas
        ingresos = df_reciente[df_reciente['tipo'] == 'ingreso']['monto'].sum()
        gastos = df_reciente[df_reciente['tipo'] == 'gasto']['monto'].sum()
        ahorro_total = ingresos - gastos
        tasa_ahorro = (ahorro_total / ingresos * 100) if ingresos > 0 else 0
        
        # Desglose de gastos
        gastos_por_cat = df_reciente[df_reciente['tipo'] == 'gasto'].groupby('categoria')['monto'].sum()
        
        # Promedio mensual
        ingresos_mensuales = ingresos / 12
        gastos_mensuales = gastos / 12
        ahorro_mensual = ahorro_total / 12
        
        # Determinar estado
        estado = self._calcular_estado_personal(tasa_ahorro, ahorro_total, gastos_por_cat, ingresos)
        
        return {
            'ingresos_anuales': float(ingresos),
            'gastos_anuales': float(gastos),
            'ahorro_total': float(ahorro_total),
            'tasa_ahorro': float(tasa_ahorro),
            'ingresos_mensuales': float(ingresos_mensuales),
            'gastos_mensuales': float(gastos_mensuales),
            'ahorro_mensual': float(ahorro_mensual),
            'gastos_por_categoria': {k: float(v) for k, v in gastos_por_cat.to_dict().items()},
            'estado': estado['categoria'],
            'score': estado['score'],
            'descripcion': estado['descripcion']
        }
    
    def _calcular_estado_personal(self, tasa_ahorro, ahorro_total, gastos_por_cat, ingresos):
        """Calcula el estado de salud financiera personal"""
        score = 0
        
        # Tasa de ahorro (40 puntos máximo)
        if tasa_ahorro >= 20:
            score += 40
        elif tasa_ahorro >= 10:
            score += 30
        elif tasa_ahorro >= 5:
            score += 20
        elif tasa_ahorro >= 0:
            score += 10
        
        # Ahorro absoluto (30 puntos máximo)
        if ahorro_total >= ingresos * 0.15:  # 15% o más
            score += 30
        elif ahorro_total >= ingresos * 0.10:
            score += 20
        elif ahorro_total >= ingresos * 0.05:
            score += 10
        elif ahorro_total > 0:
            score += 5
        
        # Diversificación de gastos (30 puntos máximo)
        if 'Ahorro' in gastos_por_cat:
            score += 15
        if 'Educación' in gastos_por_cat:
            score += 10
        
        # Balance de gastos discrecionales
        discrecionales = ['Entretenimiento', 'Restaurantes']
        gasto_discrecional = sum([gastos_por_cat.get(cat, 0) for cat in discrecionales])
        if gasto_discrecional / ingresos < 0.15:  # Menos del 15%
            score += 5
        
        # Determinar categoría
        if score >= 70:
            return {
                'categoria': 'EXCELENTE',
                'score': score,
                'descripcion': 'Tus finanzas personales están en excelente estado'
            }
        elif score >= 50:
            return {
                'categoria': 'BUENO',
                'score': score,
                'descripcion': 'Tienes una buena salud financiera'
            }
        elif score >= 30:
            return {
                'categoria': 'REGULAR',
                'score': score,
                'descripcion': 'Hay áreas de mejora en tus finanzas'
            }
        else:
            return {
                'categoria': 'CRÍTICO',
                'score': score,
                'descripcion': 'Necesitas tomar acción urgente en tus finanzas'
            }
    
    # ========================================
    # RECOMENDACIONES INTELIGENTES
    # ========================================
    
    def get_recomendaciones_empresa(self, analysis):
        """Genera recomendaciones para la empresa basadas en análisis"""
        
        if not analysis:
            return []
        
        recomendaciones = []
        estado = analysis['estado']
        margen = analysis['margen_utilidad']
        crecimiento = analysis['crecimiento_trimestral']
        gastos = analysis['gastos_por_categoria']
        
        # Análisis de estado
        if estado in ['EXCELENTE', 'BUENO']:
            # Empresa saludable - Oportunidades de crecimiento
            recomendaciones.append({
                'tipo': 'INVERSIÓN',
                'prioridad': 'ALTA',
                'titulo': 'Expansión de Negocio',
                'descripcion': f'Con un margen de {margen:.1f}% y crecimiento positivo, es momento ideal para expandir.',
                'acciones': [
                    f'Invertir en marketing digital: ${analysis["utilidad_neta"] * 0.15:,.0f} MXN (15% de utilidad)',
                    'Contratar personal estratégico para áreas de crecimiento',
                    'Abrir nuevo canal de ventas o sucursal'
                ],
                'beneficio_esperado': f'Incremento proyectado de ingresos del 20-30% en 12 meses',
                'riesgo': 'BAJO'
            })
            
            recomendaciones.append({
                'tipo': 'INVERSIÓN',
                'prioridad': 'MEDIA',
                'titulo': 'Fondo de Emergencia Empresarial',
                'descripcion': 'Crear un colchón financiero para imprevistos.',
                'acciones': [
                    f'Reservar ${analysis["gastos_anuales"] * 0.25:,.0f} MXN (3 meses de operación)',
                    'Invertir en CETES a 28 días para liquidez',
                    'Mantener línea de crédito disponible sin usar'
                ],
                'beneficio_esperado': 'Seguridad financiera y mejor calificación crediticia',
                'riesgo': 'NULO'
            })
            
            if margen > 15:
                recomendaciones.append({
                    'tipo': 'INVERSIÓN',
                    'prioridad': 'MEDIA',
                    'titulo': 'Diversificación de Ingresos',
                    'descripcion': 'Con márgenes saludables, diversificar fuentes de ingreso.',
                    'acciones': [
                        'Desarrollar nuevo producto/servicio complementario',
                        'Explorar mercados adyacentes',
                        f'Presupuesto de I+D: ${analysis["ingresos_anuales"] * 0.05:,.0f} MXN (5% de ingresos)'
                    ],
                    'beneficio_esperado': 'Reducción de riesgo y nuevas fuentes de ingreso',
                    'riesgo': 'MEDIO'
                })
        
        elif estado == 'REGULAR':
            # Empresa necesita optimización
            recomendaciones.append({
                'tipo': 'OPTIMIZACIÓN',
                'prioridad': 'ALTA',
                'titulo': 'Reducción de Gastos Operativos',
                'descripcion': f'Margen de {margen:.1f}% indica necesidad de optimizar costos.',
                'acciones': [
                    'Renegociar contratos con proveedores principales',
                    f'Meta de reducción: ${analysis["gastos_anuales"] * 0.10:,.0f} MXN (10% de gastos)',
                    'Automatizar procesos repetitivos'
                ],
                'beneficio_esperado': f'Aumento del margen a {margen + 10:.1f}%',
                'riesgo': 'BAJO'
            })
            
            # Identificar categoría de mayor gasto
            mayor_gasto = max(gastos.items(), key=lambda x: x[1])
            recomendaciones.append({
                'tipo': 'OPTIMIZACIÓN',
                'prioridad': 'ALTA',
                'titulo': f'Optimizar {mayor_gasto[0]}',
                'descripcion': f'{mayor_gasto[0]} representa tu mayor gasto: ${mayor_gasto[1]:,.0f} MXN anual.',
                'acciones': [
                    f'Analizar alternativas más económicas en {mayor_gasto[0]}',
                    'Implementar controles de gasto',
                    f'Meta de reducción: ${mayor_gasto[1] * 0.15:,.0f} MXN (15%)'
                ],
                'beneficio_esperado': 'Liberación de capital para áreas estratégicas',
                'riesgo': 'BAJO'
            })
            
            recomendaciones.append({
                'tipo': 'FINANCIAMIENTO',
                'prioridad': 'MEDIA',
                'titulo': 'Crédito para Capital de Trabajo',
                'descripcion': 'Mejorar flujo de caja con financiamiento estratégico.',
                'acciones': [
                    f'Línea de crédito de ${analysis["ingresos_anuales"] * 0.15:,.0f} MXN',
                    'Usar solo para cubrir desfases de flujo',
                    'Mantener utilización menor al 30%'
                ],
                'beneficio_esperado': 'Mejor flujo de efectivo y oportunidades de descuentos por pronto pago',
                'riesgo': 'MEDIO'
            })
        
        else:  # CRÍTICO
            # Empresa en problemas - Acción urgente
            recomendaciones.append({
                'tipo': 'URGENTE',
                'prioridad': 'CRÍTICA',
                'titulo': 'Plan de Rescate Financiero',
                'descripcion': 'Estado crítico requiere acción inmediata.',
                'acciones': [
                    'Renegociar deudas existentes',
                    f'Reducir gastos fijos en ${analysis["gastos_anuales"] * 0.30:,.0f} MXN (30%)',
                    'Acelerar cobranza - ofrecer descuentos por pronto pago'
                ],
                'beneficio_esperado': 'Estabilización en 3-6 meses',
                'riesgo': 'ALTO si no se actúa'
            })
            
            recomendaciones.append({
                'tipo': 'FINANCIAMIENTO',
                'prioridad': 'ALTA',
                'titulo': 'Reestructuración de Deuda',
                'descripcion': 'Consolidar obligaciones para mejorar flujo.',
                'acciones': [
                    'Negociar con acreedores para extender plazos',
                    'Buscar crédito de consolidación a mejor tasa',
                    'Implementar plan de pago estructurado'
                ],
                'beneficio_esperado': 'Reducción de presión de flujo mensual',
                'riesgo': 'MEDIO'
            })
        
        # Recomendación universal de tecnología
        if 'servicios' in gastos:
            recomendaciones.append({
                'tipo': 'TECNOLOGÍA',
                'prioridad': 'MEDIA',
                'titulo': 'Digitalización de Procesos',
                'descripcion': 'Inversión tecnológica para eficiencia.',
                'acciones': [
                    'Implementar ERP/CRM según tamaño',
                    f'Inversión inicial: ${analysis["ingresos_anuales"] * 0.03:,.0f} MXN',
                    'ROI esperado en 18-24 meses'
                ],
                'beneficio_esperado': 'Reducción de 20-30% en costos administrativos',
                'riesgo': 'BAJO'
            })
        
        return recomendaciones
    
    def get_recomendaciones_personal(self, analysis):
        """Genera recomendaciones personales basadas en análisis"""
        
        if not analysis:
            return []
        
        recomendaciones = []
        estado = analysis['estado']
        tasa_ahorro = analysis['tasa_ahorro']
        ahorro_mensual = analysis['ahorro_mensual']
        ingresos_mensuales = analysis['ingresos_mensuales']
        gastos = analysis['gastos_por_categoria']
        
        # Análisis de estado
        if estado in ['EXCELENTE', 'BUENO']:
            # Finanzas saludables - Oportunidades de inversión
            recomendaciones.append({
                'tipo': 'INVERSIÓN',
                'prioridad': 'ALTA',
                'titulo': 'Portafolio de Inversión Diversificado',
                'descripcion': f'Con tasa de ahorro del {tasa_ahorro:.1f}%, puedes construir patrimonio.',
                'acciones': [
                    f'CETES: ${ahorro_mensual * 0.30:,.0f} MXN/mes (30% - liquidez)',
                    f'Fondos indexados S&P 500: ${ahorro_mensual * 0.40:,.0f} MXN/mes (40% - crecimiento)',
                    f'FIBRAS: ${ahorro_mensual * 0.30:,.0f} MXN/mes (30% - ingresos pasivos)'
                ],
                'beneficio_esperado': 'Retorno anual proyectado del 8-12%',
                'riesgo': 'MEDIO'
            })
            
            recomendaciones.append({
                'tipo': 'INVERSIÓN',
                'prioridad': 'ALTA',
                'titulo': 'Fondo de Emergencia Completo',
                'descripcion': 'Asegura tu estabilidad financiera.',
                'acciones': [
                    f'Meta: ${ingresos_mensuales * 6:,.0f} MXN (6 meses de gastos)',
                    f'Ahorro actual proyectado: ${ahorro_mensual * 12:,.0f} MXN/año',
                    'Mantener en CETES o cuenta de ahorro de alto rendimiento'
                ],
                'beneficio_esperado': 'Tranquilidad financiera ante imprevistos',
                'riesgo': 'NULO'
            })
            
            if tasa_ahorro > 20:
                recomendaciones.append({
                    'tipo': 'INVERSIÓN',
                    'prioridad': 'MEDIA',
                    'titulo': 'Inversión Inmobiliaria',
                    'descripcion': 'Considera bienes raíces para diversificar.',
                    'acciones': [
                        f'Ahorro en 3 años: ${ahorro_mensual * 36:,.0f} MXN',
                        'Suficiente para enganche de propiedad',
                        'Aprovechar crédito hipotecario a tasa baja'
                    ],
                    'beneficio_esperado': 'Patrimonio + Plusvalía + Ingreso por renta',
                    'riesgo': 'MEDIO-BAJO'
                })
        
        elif estado == 'REGULAR':
            # Necesita optimización
            recomendaciones.append({
                'tipo': 'OPTIMIZACIÓN',
                'prioridad': 'ALTA',
                'titulo': 'Plan de Ahorro Sistemático',
                'descripcion': f'Tasa de ahorro de {tasa_ahorro:.1f}% debe incrementarse.',
                'acciones': [
                    'Meta: Incrementar ahorro al 15% de ingresos',
                    f'Esto significa ahorrar ${ingresos_mensuales * 0.15:,.0f} MXN/mes',
                    'Automatizar transferencia el día de pago'
                ],
                'beneficio_esperado': f'Acumulación de ${ingresos_mensuales * 0.15 * 12:,.0f} MXN en 1 año',
                'riesgo': 'NULO'
            })
            
            # Analizar gastos discrecionales
            discrecionales = ['Entretenimiento', 'Restaurantes']
            gasto_discrecional = sum([gastos.get(cat, 0) for cat in discrecionales])
            
            if gasto_discrecional > ingresos_mensuales * 12 * 0.20:
                recomendaciones.append({
                    'tipo': 'OPTIMIZACIÓN',
                    'prioridad': 'ALTA',
                    'titulo': 'Reducir Gastos Discrecionales',
                    'descripcion': f'Gastos en entretenimiento/restaurantes: ${gasto_discrecional:,.0f} MXN/año.',
                    'acciones': [
                        f'Reducir 30%: Ahorro de ${gasto_discrecional * 0.30:,.0f} MXN/año',
                        'Establecer presupuesto mensual de gastos opcionales',
                        'Buscar alternativas gratuitas o de bajo costo'
                    ],
                    'beneficio_esperado': 'Liberación de capital para ahorro/inversión',
                    'riesgo': 'NULO'
                })
            
            recomendaciones.append({
                'tipo': 'EDUCACIÓN',
                'prioridad': 'MEDIA',
                'titulo': 'Incrementar Ingresos',
                'descripcion': 'La mejor inversión: en ti mismo.',
                'acciones': [
                    'Certificación profesional o curso técnico',
                    f'Inversión recomendada: ${ingresos_mensuales * 1.5:,.0f} MXN',
                    'ROI esperado: +20-30% en ingresos en 12 meses'
                ],
                'beneficio_esperado': f'Aumento de ingresos de ${ingresos_mensuales * 0.25:,.0f} MXN/mes',
                'riesgo': 'BAJO'
            })
        
        else:  # CRÍTICO
            # Situación difícil - Plan de rescate
            recomendaciones.append({
                'tipo': 'URGENTE',
                'prioridad': 'CRÍTICA',
                'titulo': 'Plan de Rescate Financiero Personal',
                'descripcion': 'Necesitas tomar acción inmediata.',
                'acciones': [
                    'Crear presupuesto estricto de supervivencia',
                    'Eliminar TODOS los gastos no esenciales',
                    f'Meta mínima de ahorro: ${ingresos_mensuales * 0.05:,.0f} MXN/mes (5%)'
                ],
                'beneficio_esperado': 'Estabilización en 6 meses',
                'riesgo': 'ALTO si no se actúa'
            })
            
            recomendaciones.append({
                'tipo': 'FINANCIAMIENTO',
                'prioridad': 'ALTA',
                'titulo': 'Consolidación de Deudas',
                'descripcion': 'Si tienes deudas, consolida para menor tasa.',
                'acciones': [
                    'Negociar con bancos para reducir tasas',
                    'Considerar préstamo de consolidación',
                    'Eliminar primero deudas de mayor interés'
                ],
                'beneficio_esperado': 'Reducción de intereses y presión mensual',
                'riesgo': 'MEDIO'
            })
            
            recomendaciones.append({
                'tipo': 'INGRESOS',
                'prioridad': 'ALTA',
                'titulo': 'Fuente de Ingresos Adicional',
                'descripcion': 'Considera trabajo adicional temporal.',
                'acciones': [
                    'Freelance en tu área de expertis',
                    'Venta de artículos no esenciales',
                    'Trabajo de medio tiempo los fines de semana'
                ],
                'beneficio_esperado': f'Ingresos extra de ${ingresos_mensuales * 0.30:,.0f} MXN/mes',
                'riesgo': 'BAJO'
            })
        
        # Recomendación universal
        if 'Ahorro' not in gastos or gastos.get('Ahorro', 0) < ingresos_mensuales * 12 * 0.10:
            recomendaciones.append({
                'tipo': 'AHORRO',
                'prioridad': 'ALTA' if estado != 'CRÍTICO' else 'MEDIA',
                'titulo': 'AFORE y Retiro',
                'descripcion': 'Nunca es tarde para pensar en el retiro.',
                'acciones': [
                    f'Aportación voluntaria mensual: ${ingresos_mensuales * 0.05:,.0f} MXN (5%)',
                    'Deducible de impuestos',
                    'Crecimiento con interés compuesto'
                ],
                'beneficio_esperado': 'Seguridad en el futuro + ahorro fiscal',
                'riesgo': 'NULO'
            })
        
        return recomendaciones
    
    # ========================================
    # ANÁLISIS COMPLETO
    # ========================================
    
    def get_analisis_completo(self, empresa_id=None, usuario_id=None):
        """Análisis completo con recomendaciones"""
        
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'empresa': None,
            'personal': None,
            'recomendaciones_empresa': [],
            'recomendaciones_personal': [],
            'resumen_ejecutivo': ''
        }
        
        # Análisis empresarial
        if empresa_id or True:  # Si no hay ID, analizar todas
            empresa_analysis = self.analyze_empresa(empresa_id)
            if empresa_analysis:
                resultado['empresa'] = empresa_analysis
                resultado['recomendaciones_empresa'] = self.get_recomendaciones_empresa(empresa_analysis)
        
        # Análisis personal
        if usuario_id or True:
            personal_analysis = self.analyze_personal(usuario_id)
            if personal_analysis:
                resultado['personal'] = personal_analysis
                resultado['recomendaciones_personal'] = self.get_recomendaciones_personal(personal_analysis)
        
        # Generar resumen ejecutivo
        resultado['resumen_ejecutivo'] = self._generar_resumen(resultado)
        
        return resultado
    
    def _generar_resumen(self, resultado):
        """Genera resumen ejecutivo del análisis"""
        
        resumen_partes = []
        
        # Resumen empresarial
        if resultado['empresa']:
            emp = resultado['empresa']
            resumen_partes.append(
                f"**EMPRESA**: Estado {emp['estado']} (Score: {emp['score']}/100). "
                f"Margen de utilidad del {emp['margen_utilidad']:.1f}% con "
                f"{'crecimiento' if emp['crecimiento_trimestral'] > 0 else 'decrecimiento'} "
                f"del {abs(emp['crecimiento_trimestral']):.1f}% trimestral."
            )
        
        # Resumen personal
        if resultado['personal']:
            per = resultado['personal']
            resumen_partes.append(
                f"**PERSONAL**: Estado {per['estado']} (Score: {per['score']}/100). "
                f"Tasa de ahorro del {per['tasa_ahorro']:.1f}% con ahorro mensual de "
                f"${per['ahorro_mensual']:,.0f} MXN."
            )
        
        # Conteo de recomendaciones
        total_recs = len(resultado['recomendaciones_empresa']) + len(resultado['recomendaciones_personal'])
        resumen_partes.append(f"\n\n**RECOMENDACIONES**: {total_recs} acciones estratégicas identificadas.")
        
        return ' '.join(resumen_partes)


# Instancia global
_advisor_instance = None

def get_advisor():
    """Obtener instancia del asesor financiero"""
    global _advisor_instance
    if _advisor_instance is None:
        _advisor_instance = FinancialAdvisor()
    return _advisor_instance
