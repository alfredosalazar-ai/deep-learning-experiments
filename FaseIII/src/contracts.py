"""Validate the published Fase II API response schema using synthetic examples only."""
import json
REQUIRED={'clase_predicha','decision_operativa','requiere_revision_humana','puntaje_individual','umbral_individual','version_modelo','advertencia'}
LABELS={'INDIVIDUAL','PAQUETE','AMBIGUA','FUERA_ALCANCE'}
def check_response(payload):
    if not isinstance(payload,dict): raise ValueError('Respuesta no es JSON object')
    missing=REQUIRED-set(payload)
    if missing: raise ValueError(f'Campos faltantes: {sorted(missing)}')
    if payload['clase_predicha'] not in LABELS: raise ValueError('Clase fuera de catalogo')
    if payload['decision_operativa'] not in {'REVISION_HUMANA','FLUJO_INDIVIDUAL'}:
        raise ValueError('Decision desconocida')
    if type(payload['requiere_revision_humana']) is not bool: raise ValueError('Revision no booleana')
    score=float(payload['puntaje_individual']);threshold=float(payload['umbral_individual'])
    if not 0<=score<=1 or not 0<=threshold<=1: raise ValueError('Puntajes fuera de [0,1]')
    if payload['decision_operativa']=='FLUJO_INDIVIDUAL':
        if payload['clase_predicha']!='INDIVIDUAL' or score<threshold or payload['requiere_revision_humana']:
            raise ValueError('Falsa elegibilidad conforme a politica declarada')
    if payload['decision_operativa']=='REVISION_HUMANA' and not payload['requiere_revision_humana']:
        raise ValueError('Revision humana inconsistente')
    return True
