# app/backend/financial_api.py
"""
API adicional para análisis financiero
"""

from flask import Blueprint, jsonify, request
from modules.financial_advisor import get_advisor

financial_bp = Blueprint('financial', __name__)
advisor = get_advisor()

@financial_bp.route('/analisis/empresa', methods=['GET'])
def analisis_empresa():
    """Análisis financiero de empresa"""
    empresa_id = request.args.get('empresa_id')
    
    try:
        analysis = advisor.analyze_empresa(empresa_id)
        recomendaciones = advisor.get_recomendaciones_empresa(analysis)
        
        return jsonify({
            'success': True,
            'analisis': analysis,
            'recomendaciones': recomendaciones
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@financial_bp.route('/analisis/personal', methods=['GET'])
def analisis_personal():
    """Análisis financiero personal"""
    usuario_id = request.args.get('usuario_id')
    
    try:
        analysis = advisor.analyze_personal(usuario_id)
        recomendaciones = advisor.get_recomendaciones_personal(analysis)
        
        return jsonify({
            'success': True,
            'analisis': analysis,
            'recomendaciones': recomendaciones
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@financial_bp.route('/analisis/completo', methods=['GET'])
def analisis_completo():
    """Análisis completo con recomendaciones"""
    empresa_id = request.args.get('empresa_id')
    usuario_id = request.args.get('usuario_id')
    
    try:
        resultado = advisor.get_analisis_completo(empresa_id, usuario_id)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@financial_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Dashboard financiero resumido"""
    try:
        # Análisis de todos los datos
        empresa_analysis = advisor.analyze_empresa()
        personal_analysis = advisor.analyze_personal()
        
        # Crear dashboard resumido
        dashboard_data = {
            'empresa': {
                'estado': empresa_analysis['estado'],
                'score': empresa_analysis['score'],
                'margen_utilidad': empresa_analysis['margen_utilidad'],
                'crecimiento': empresa_analysis['crecimiento_trimestral'],
                'utilidad_anual': empresa_analysis['utilidad_neta']
            },
            'personal': {
                'estado': personal_analysis['estado'],
                'score': personal_analysis['score'],
                'tasa_ahorro': personal_analysis['tasa_ahorro'],
                'ahorro_mensual': personal_analysis['ahorro_mensual'],
                'ingresos_mensuales': personal_analysis['ingresos_mensuales']
            },
            'alertas': []
        }
        
        # Generar alertas
        if empresa_analysis['estado'] in ['CRÍTICO', 'REGULAR']:
            dashboard_data['alertas'].append({
                'tipo': 'empresa',
                'nivel': 'alta' if empresa_analysis['estado'] == 'CRÍTICO' else 'media',
                'mensaje': f"Empresa en estado {empresa_analysis['estado']}: requiere atención"
            })
        
        if personal_analysis['tasa_ahorro'] < 10:
            dashboard_data['alertas'].append({
                'tipo': 'personal',
                'nivel': 'media',
                'mensaje': f"Tasa de ahorro baja ({personal_analysis['tasa_ahorro']:.1f}%): aumentar al 15%"
            })
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
