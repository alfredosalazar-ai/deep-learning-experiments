"""Recalcula y contrasta metricas de CIMA desde los CSV exportados por Colab.

Ejecutar desde cualquier directorio:
    python src/evaluation.py
No ejecuta modelos ni necesita GPU.
"""
from pathlib import Path
import sys
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, recall_score

ROOT = Path(__file__).resolve().parents[1]
PRED = ROOT / 'results' / 'predictions.csv'
METRICS = ROOT / 'results' / 'metrics.csv'
CLASSES = ['INDIVIDUAL', 'PAQUETE', 'AMBIGUA', 'FUERA_ALCANCE']
TOL = 1e-5


def evaluar():
    if not PRED.is_file() or not METRICS.is_file():
        raise FileNotFoundError('Se requieren results/predictions.csv y results/metrics.csv')
    pred = pd.read_csv(PRED, encoding='utf-8-sig')
    saved = pd.read_csv(METRICS, encoding='utf-8-sig')
    for col in ['id', 'modelo', 'clase_real', 'prediccion']:
        if col not in pred.columns:
            raise ValueError(f'Columna ausente en predictions.csv: {col}')
    for col in ['modelo', 'accuracy', 'precision_macro', 'recall_macro', 'f1_macro',
                'precision_weighted', 'recall_weighted', 'f1_weighted',
                'falsa_elegibilidad_n', 'tasa_falsa_elegibilidad', 'recall_individual', 'n_evaluacion']:
        if col not in saved.columns:
            raise ValueError(f'Columna ausente en metrics.csv: {col}')
    if pred[['id','modelo']].duplicated().any():
        raise ValueError('Hay predicciones duplicadas para la misma combinacion id/modelo')
    if saved['modelo'].duplicated().any():
        raise ValueError('metrics.csv tiene modelos repetidos')
    if set(pred['modelo']) != set(saved['modelo']):
        raise ValueError('Los modelos de predictions.csv y metrics.csv no coinciden')
    if not pred['clase_real'].isin(CLASSES).all() or not pred['prediccion'].isin(CLASSES).all():
        raise ValueError('Se encontraron etiquetas fuera del conjunto de cuatro clases')
    if pred[['clase_real','prediccion']].isna().any().any():
        raise ValueError('Hay etiquetas vacias')
    items = []
    for model, group in pred.groupby('modelo', sort=True):
        y = group['clase_real']
        yhat = group['prediccion']
        pm, rm, fm, _ = precision_recall_fscore_support(
            y, yhat, labels=CLASSES, average='macro', zero_division=0)
        pw, rw, fw, _ = precision_recall_fscore_support(
            y, yhat, labels=CLASSES, average='weighted', zero_division=0)
        nonindividual = y != 'INDIVIDUAL'
        denominator = int(nonindividual.sum())
        false_n = int((nonindividual & (yhat == 'INDIVIDUAL')).sum())
        row = {
            'modelo': model,
            'accuracy': accuracy_score(y, yhat),
            'precision_macro': pm,
            'recall_macro': rm,
            'f1_macro': fm,
            'precision_weighted': pw,
            'recall_weighted': rw,
            'f1_weighted': fw,
            'falsa_elegibilidad_n': false_n,
            'tasa_falsa_elegibilidad': false_n / denominator if denominator else float('nan'),
            'recall_individual': recall_score(y, yhat, labels=['INDIVIDUAL'], average='macro', zero_division=0),
            'n_evaluacion': len(group),
        }
        items.append(row)
    computed = pd.DataFrame(items).set_index('modelo')
    saved = saved.set_index('modelo')
    mismatches = []
    for model in computed.index:
        for metric in computed.columns:
            a, b = computed.loc[model,metric], saved.loc[model,metric]
            if pd.isna(a) or pd.isna(b) or abs(float(a) - float(b)) > TOL:
                mismatches.append((model, metric, a, b))
    print('CHATBOT CIMA - VERIFICACION DE RESULTADOS E3')
    print(computed[['accuracy','precision_macro','recall_macro','f1_macro',
                    'falsa_elegibilidad_n','tasa_falsa_elegibilidad','n_evaluacion']].round(6).to_string())
    print('\nNota: la latencia y los tiempos de carga no se recalculan desde las etiquetas.')
    if mismatches:
        print('\nDIFERENCIAS DETECTADAS:')
        for model, metric, calculated, stored in mismatches:
            print(f'- {model} / {metric}: calculado={calculated}, publicado={stored}')
        return False
    print('\nVERIFICACION SUPERADA: metricas publicadas y recalculadas coinciden.')
    return True


if __name__ == '__main__':
    try:
        sys.exit(0 if evaluar() else 1)
    except (FileNotFoundError, ValueError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
