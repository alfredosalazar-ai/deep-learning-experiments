"""Calidad predictiva con etiquetas conocidas. Demo sintética separada de evaluación real.

No usa modelos ni credenciales. La demo genera predicciones ficticias y NO describe
el desempeño de CIMA en Render. Para evidencia real, usar --csv con datos etiquetados.
"""
from __future__ import annotations
import argparse
import csv
from collections import Counter
from pathlib import Path
from .common import ROOT, utcnow, write_json
from .drift import CLASSES


def evaluar_pares(pares: list[tuple[str, str]]) -> dict:
    if not pares:
        raise ValueError('Se requiere al menos un par de etiquetas')
    for y, p in pares:
        if y not in CLASSES or p not in CLASSES:
            raise ValueError('Etiquetas fuera de las cuatro clases CIMA')
    total=len(pares)
    aciertos=sum(y==p for y,p in pares)
    detalle={}
    for clase in CLASSES:
        tp=sum(y==clase and p==clase for y,p in pares)
        fp=sum(y!=clase and p==clase for y,p in pares)
        fn=sum(y==clase and p!=clase for y,p in pares)
        precision=tp/(tp+fp) if tp+fp else 0.0
        recall=tp/(tp+fn) if tp+fn else 0.0
        f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
        detalle[clase]={'soporte':tp+fn,'precision':round(precision,4), 'recall':round(recall,4),'f1':round(f1,4),'aciertos':tp}
    negatives=sum(y!='INDIVIDUAL' for y,p in pares)
    fe=sum(y!='INDIVIDUAL' and p=='INDIVIDUAL' for y,p in pares)
    return {'n_etiquetados':total,'accuracy':round(aciertos/total,4),
            'precision_macro':round(sum(v['precision'] for v in detalle.values())/4,4),
            'recall_macro':round(sum(v['recall'] for v in detalle.values())/4,4),
            'f1_macro':round(sum(v['f1'] for v in detalle.values())/4,4),
            'falsas_elegibilidades_predichas':fe,
            'casos_no_individuales':negatives,
            'nota_riesgo':'La prediccion INDIVIDUAL no implica aceptacion automatica; faltan puntaje y regla de umbral.',
            'por_clase':detalle}


def demo_pares():
    real=list(CLASSES)*8  # 32 casos ficticios equilibrados; no es dataset del modelo.
    base=list(real)
    deteriorado=list(real)
    # 4 errores de referencia, 10 errores tras degradacion deliberada
    for j in [1,9,18,27]:
        base[j]='INDIVIDUAL' if real[j]!='INDIVIDUAL' else 'AMBIGUA'
    for j in [1,3,5,7,9,11,14,18,23,27]:
        deteriorado[j]='INDIVIDUAL' if real[j]!='INDIVIDUAL' else 'AMBIGUA'
    return list(zip(real,base)), list(zip(real,deteriorado))


def alerta_calidad(base:dict,actual:dict,limite_accuracy:float=0.80,limite_f1:float=0.80):
    alertas=[]
    for campo,limite in [('accuracy',limite_accuracy),('f1_macro',limite_f1)]:
        value=actual[campo]
        if value<limite:
            alertas.append({'codigo':'CALIDAD_'+campo.upper(),'severidad':'P1','observado':value,
                'referencia':base[campo],'umbral':limite,
                'variacion_puntos_porcentuales':round((value-base[campo])*100,2),
                'accion':'Verificar etiquetas, drift y revisión humana; no publicar modelo automáticamente'})
    return alertas


def cargar_csv(path:Path):
    pares=[]
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if not {'clase_real','clase_predicha'}.issubset(reader.fieldnames or []):
            raise ValueError('CSV requiere clase_real y clase_predicha')
        for row in reader:
            pares.append((row['clase_real'],row['clase_predicha']))
    return pares


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--csv',type=Path,help='CSV etiquetado real del experimento: clase_real,clase_predicha')
    p.add_argument('--salida',type=Path,default=ROOT/'results'/'metricas'/'calidad_demo.json')
    args=p.parse_args()
    if args.csv:
        result={'origen':'EVALUACION_CSV_ETIQUETADO','fecha_utc':utcnow(),
                'resultados':evaluar_pares(cargar_csv(args.csv)),
                'nota':'La independencia del lote de evaluacion debe verificarse externamente.'}
    else:
        antes,durante=demo_pares()
        base=evaluar_pares(antes);actual=evaluar_pares(durante)
        result={'origen':'SIMULACION_OFFLINE','fecha_utc':utcnow(),
                'descripcion':'Predicciones y etiquetas completamente ficticias: no son resultados del modelo desplegado',
                'linea_base_simulada':base,'degradado_simulado':actual,
                'alertas':alerta_calidad(base,actual)}
    write_json(args.salida,result)
    print('=== CIMA | CALIDAD PREDICTIVA ===')
    if args.csv:
        print('ORIGEN: CSV ETIQUETADO; revisar independencia de datos')
        r=result['resultados']
        print(f"n={r['n_etiquetados']} | accuracy={r['accuracy']:.4f} | F1 macro={r['f1_macro']:.4f}")
    else:
        print('ORIGEN: LABORATORIO FICTICIO (NO MODELO REAL)')
        for name,r in [('BASE',base),('DEGRADADO',actual)]:
            print(f"{name:10s} accuracy={r['accuracy']:.4f} | F1 macro={r['f1_macro']:.4f} | falsas INDIVIDUAL={r['falsas_elegibilidades_predichas']}")
        for alert in result['alertas']:
            print(f"[ALERTA {alert['severidad']}] {alert['codigo']}: observado={alert['observado']:.4f} | base={alert['referencia']:.4f} | umbral={alert['umbral']:.4f}")
    print('Salida:',args.salida)

if __name__=='__main__':main()
