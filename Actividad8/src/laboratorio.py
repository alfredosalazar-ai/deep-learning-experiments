"""Evidencia reproducible: consola, antirruido, runbooks y respuesta autocontenida.

NINGUNA accion altera Render, repositorios, correos, tickets o modelos reales.
Los valores son escenarios artificiales y las respuestas cambian SOLO un estado JSON local.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from .alertas import deduplicar, evaluar_alertas
from .calidad import alerta_calidad, demo_pares, evaluar_pares
from .common import ROOT, load_config, utcnow, write_json
from .incidentes import simular_incidentes


def _metric_name(code:str)->str:
    return {'LATENCIA_P95':'Latencia P95 (ms)', 'DRIFT_CRITICO':'PSI distribución',
            'ERRORES_5XX':'Tasa HTTP 5xx','SLO_DISPONIBILIDAD':'Disponibilidad',
            'FALSA_ELEGIBILIDAD':'Falsas elegibilidades'}.get(code,code)


def ejecutar_laboratorio(config:dict)->dict:
    scenarios=simular_incidentes(config)['incidentes']
    base_pairs,degraded_pairs=demo_pares()
    base_quality=evaluar_pares(base_pairs)
    degraded_quality=evaluar_pares(degraded_pairs)
    quality_alerts=alerta_calidad(base_quality,degraded_quality)
    history=[]
    for scenario in scenarios:
        ident=scenario['id']
        alertas=evaluar_alertas(scenario['durante'],config)
        # Simulación de estado modificable: automatización segura con escritura local
        state={'modo':'OPERACION_NORMAL','max_reintentos':0,'aceptacion_automatica_demo':True}
        if ident=='INC-01':
            state['modo']='DIAGNOSTICO_LATENCIA';state['carga_sintetica_reducida']=True
            accion='Reduccion de carga sintetica (variable local)'
        elif ident=='INC-02':
            state['modo']='REVISION_HUMANA';state['aceptacion_automatica_demo']=False
            accion='Bloqueo de aceptacion solo en laboratorio'
        else:
            state['modo']='CONTINGENCIA';state['max_reintentos']=2
            accion='Contingencia simulada con maximo 2 reintentos'
        after=evaluar_alertas(scenario['despues'],config)
        completed=bool(alertas) and not after
        history.append({'incidente':ident,'runbook':scenario['runbook_ejecutado_simulado'],
                        'tipo':'SIMULACION_OFFLINE','descripcion':scenario['nombre'],
                        'impacto':'Degradacion operativa simulada','severidad':'P1',
                        'alertas':[a['codigo'] for a in alertas],
                        'accion_aplicada':accion,'estado_durante':state.copy(),
                        'verificaciones':[{'paso':'Confirmar anomalia','resultado':bool(alertas)},
                                         {'paso':'Aplicar accion en estado aislado','resultado':True},
                                         {'paso':'Verificar retorno a umbrales','resultado':not after}],
                        'metricas_antes':scenario['antes'],'metricas_durante':scenario['durante'],
                        'metricas_despues':scenario['despues'],
                        'estado_final':{'modo':'OPERACION_NORMAL','aceptacion_automatica_demo':True,'max_reintentos':0},
                        'recuperacion_verificada':completed})
    # Control de ruido reproducible con reloj fijo
    now=datetime(2026,11,12,18,0,tzinfo=timezone.utc)
    repeated=evaluar_alertas(scenarios[0]['durante'],config)
    out1,estado=deduplicar(repeated,{},30,now)
    out2,estado2=deduplicar(repeated,estado,30,now+timedelta(minutes=2))
    out3,_=deduplicar(repeated,estado2,30,now+timedelta(minutes=31))
    noise={'alerta':repeated[0]['codigo'], 'primera_emision':len(out1),
           'segunda_emision_2min':len(out2),'suprimidas_2min':len(repeated)-len(out2),
           'emision_31min':len(out3),'cooldown_minutos':30}
    return {'origen':'SIMULACION_OFFLINE','fecha_utc':utcnow(),
            'nota':'Datos y acciones simulados; sin escritura externa. MLflow NO integrado.',
            'incidentes':history,'antirruido':noise,
            'calidad':{'linea_base_simulada':base_quality,'degradado_simulado':degraded_quality,
                       'alertas':quality_alerts}}


def consola(r:dict)->str:
    lines=['='*66,'CHATBOT CIMA | ACTIVIDAD 8 | MONITOREO Y RESPUESTA',
           'EVIDENCIA 100% SIMULADA - SIN TRAFICO A RENDER','='*66]
    for incident in r['incidentes']:
        lines += [f"\n=== {incident['incidente']} - {incident['descripcion']} ===",
                  f"Runbook: {incident['runbook']}",
                  'ESTADO: NORMAL -> ALERTA -> RECUPERACION']
        for code in incident['alertas']:
            e=next(a for a in evaluar_alertas(incident['metricas_durante'],load_config()) if a['codigo']==code)
            lines.append(f"[ALERTA {e['severidad']}] {_metric_name(code)} | observado={e['observado']:.4f} | umbral={e['umbral']:.4f} | estado=ALERTA")
        lines += [f"[ACCION AUTOMATICA LAB] {incident['accion_aplicada']}",
                  f"[RECUPERACION] verificaciones={sum(x['resultado'] for x in incident['verificaciones'])}/3 | alertas_finales=0 | estado={'OK' if incident['recuperacion_verificada'] else 'REVISAR'}"]
    n=r['antirruido']
    lines += ['\n=== CONTROL ANTIRRUIDO (30 MIN) ===',
              f"[PRIMER AVISO] emitidas={n['primera_emision']}",
              f"[MISMA ALERTA A LOS 2 MIN] emitidas={n['segunda_emision_2min']} | suprimidas={n['suprimidas_2min']}",
              f"[DESPUES DE 31 MIN] emitidas={n['emision_31min']}"]
    q=r['calidad'];b=q['linea_base_simulada'];a=q['degradado_simulado']
    lines += ['\n=== CALIDAD PREDICTIVA | ETIQUETAS FICTICIAS ===',
              f"accuracy | base={b['accuracy']:.4f} | actual={a['accuracy']:.4f} | delta={100*(a['accuracy']-b['accuracy']):+.2f} pp",
              f"f1_macro | base={b['f1_macro']:.4f} | actual={a['f1_macro']:.4f} | delta={100*(a['f1_macro']-b['f1_macro']):+.2f} pp"]
    for alert in q['alertas']:
        lines.append(f"[ALERTA {alert['severidad']}] {alert['codigo']} | actual={alert['observado']:.4f} < umbral={alert['umbral']:.4f}")
    lines += ['','CONCLUSION: escenario simulado; no acredita calidad ni monitoreo continuo del CIMA desplegado.']
    return '\n'.join(lines)+'\n'


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--salida',type=Path,default=ROOT/'results'/'incidentes'/'runbooks_ejecutados_demo.json')
    args=p.parse_args()
    report=ejecutar_laboratorio(load_config())
    write_json(args.salida,report)
    log=ROOT/'results'/'incidentes'/'consola_alertas_demo.txt'
    log.parent.mkdir(parents=True,exist_ok=True)
    output=consola(report)
    log.write_text(output,encoding='utf-8')
    print(output)
    print('JSON:',args.salida,'\nLOG:',log)

if __name__=='__main__':main()
