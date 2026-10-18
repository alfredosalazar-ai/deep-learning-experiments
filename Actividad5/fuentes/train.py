"""Entrena dos clasificadores NLP y registra GridSearchCV, modelos y artefactos en MLflow.

Uso (desde cualquier directorio): python Actividad5/fuentes/train.py
Los 26 textos de prueba se utilizan una sola vez tras elegir hiperparametros con CV.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import time
from pathlib import Path
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score, make_scorer
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import label_binarize
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / 'datos' / 'datos_limp' / 'cima_consultas_limpias.csv'
RESULTS = ROOT / 'resultados' / 'entrenamiento'
LABELS = ['INDIVIDUAL', 'PAQUETE', 'AMBIGUA', 'FUERA_ALCANCE']
SEED = 20261015


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_data(path):
    d = pd.read_csv(path, encoding='utf-8-sig', keep_default_na=False)
    required = {'texto_normalizado', 'clase_real', 'particion_a5'}
    if not required.issubset(d):
        raise ValueError(f'Faltan campos: {required-set(d.columns)}')
    if len(d) != 128 or d.texto_normalizado.eq('').any() or len(set(d.clase_real)-set(LABELS)):
        raise ValueError('Dataset incompatible con la version de Actividad 5')
    train = d[d.particion_a5 == 'entrenamiento'].copy()
    test = d[d.particion_a5 == 'prueba'].copy()
    if len(train) != 102 or len(test) != 26:
        raise ValueError('Particiones diferentes de 102/26')
    k1 = set(train.texto_normalizado.str.casefold())
    k2 = set(test.texto_normalizado.str.casefold())
    if k1 & k2:
        raise ValueError('Fuga de textos entre entrenamiento y prueba')
    return train, test


def specs():
    vect = {'tfidf__ngram_range': [(1, 1), (1, 2)], 'tfidf__min_df': [1, 2], 'tfidf__sublinear_tf': [True]}
    return {
        'Regresion_Logistica': (LogisticRegression(max_iter=1500, random_state=SEED), {**vect, 'clf__C': [0.1, 1, 10], 'clf__class_weight': [None, 'balanced']}),
        'LinearSVC': (LinearSVC(random_state=SEED, max_iter=10000), {**vect, 'clf__C': [0.1, 1, 10], 'clf__class_weight': [None, 'balanced']}),
    }


def auc_scores(model, x_test, y_test):
    """Macro one-vs-rest AUC from ranking scores; not calibrated probabilities for SVC."""
    xscore = model.decision_function(x_test) if hasattr(model, 'decision_function') else model.predict_proba(x_test)
    labels = list(model.classes_)
    y_binary = label_binarize(y_test, classes=labels)
    if y_binary.shape[1] != len(labels):
        return float('nan')
    return float(roc_auc_score(y_binary, xscore, average='macro'))


def main(data_path=DEFAULT_DATA, output=RESULTS):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    train, test = load_data(data_path)
    train_x, train_y = train.texto_normalizado.tolist(), train.clase_real.tolist()
    test_x, test_y = test.texto_normalizado.tolist(), test.clase_real.tolist()
    cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=SEED)
    tracking_db = (ROOT / "mlflow.db").resolve()
    tracking_uri = f"sqlite:///{tracking_db.as_posix()}"
    mlflow.set_tracking_uri(tracking_uri)
    print("MLflow Tracking URI:", tracking_uri)
    mlflow.set_experiment('CIMA_Actividad5_NLP_Supervisado')
    records, predictions = [], []
    for model_name, (est, grid) in specs().items():
        pipe = Pipeline([('tfidf', TfidfVectorizer(lowercase=True, strip_accents=None)), ('clf', est)])
        gs = GridSearchCV(pipe, grid, scoring='f1_macro', cv=cv, n_jobs=-1, refit=True, return_train_score=True)
        with mlflow.start_run(run_name=model_name):
            mlflow.set_tags({'dataset_version':'a5-v1.0','task':'intent_classification','source':'synthetic_public_cima','evaluation':'holdout_untouched_before_CV','model_family':model_name})
            mlflow.log_param('dataset_sha256', sha256(data_path))
            mlflow.log_param('seed', SEED)
            mlflow.log_param('n_train', len(train))
            mlflow.log_param('n_test', len(test))
            mlflow.log_param('cv_folds', 4)
            start = time.perf_counter()
            gs.fit(train_x, train_y)
            fit_seconds = time.perf_counter() - start
            best = gs.best_estimator_
            t0 = time.perf_counter()
            pred = best.predict(test_x)
            latency_ms = 1000*(time.perf_counter()-t0)/len(test_x)
            values = {
                'accuracy': accuracy_score(test_y,pred),
                'precision_macro': precision_score(test_y,pred,labels=LABELS,average='macro',zero_division=0),
                'recall_macro': recall_score(test_y,pred,labels=LABELS,average='macro',zero_division=0),
                'f1_macro': f1_score(test_y,pred,labels=LABELS,average='macro',zero_division=0),
                'roc_auc_ovr_macro_scores': auc_scores(best,test_x,test_y),
                'cv_best_f1_macro': gs.best_score_,
                'cv_best_f1_std': gs.cv_results_['std_test_score'][gs.best_index_],
                'fit_seconds': fit_seconds,
                'prediction_latency_ms_per_text_batch': latency_ms,
                'false_eligibility_count': int(sum(a!='INDIVIDUAL' and b=='INDIVIDUAL' for a,b in zip(test_y,pred))),
                'false_eligibility_rate': float(sum(a!='INDIVIDUAL' and b=='INDIVIDUAL' for a,b in zip(test_y,pred))/sum(a!='INDIVIDUAL' for a in test_y)),
            }
            for key,value in gs.best_params_.items():
                mlflow.log_param(key,str(value))
            mlflow.log_metrics(values)
            model_dir = output / 'modelos'
            model_dir.mkdir(exist_ok=True)
            joblib.dump(best, model_dir / f'{model_name}.joblib')
            mlflow.sklearn.log_model(best, name='modelo_entrenado')
            cv_df = pd.DataFrame(gs.cv_results_)
            cv_path = output / f'gridsearch_{model_name}.csv'
            cv_df.to_csv(cv_path,index=False)
            mlflow.log_artifact(str(cv_path), artifact_path='busqueda')
            fig, ax = plt.subplots(figsize=(7,5))
            cm = confusion_matrix(test_y,pred,labels=LABELS)
            im=ax.imshow(cm)
            ax.set_xticks(range(4),LABELS,rotation=35,ha='right')
            ax.set_yticks(range(4),LABELS)
            for i in range(4):
                for j in range(4):
                    ax.text(j,i,str(cm[i,j]),ha='center',va='center')
            ax.set(xlabel='Prediccion',ylabel='Real',title=f'CIMA Actividad 5 - {model_name}')
            fig.tight_layout()
            fig_path = output / f'matriz_{model_name}.png'
            fig.savefig(fig_path,dpi=160)
            plt.close(fig)
            mlflow.log_artifact(str(fig_path),artifact_path='graficos')
            rep_path = output / f'reporte_{model_name}.json'
            rep_path.write_text(json.dumps(classification_report(test_y,pred,labels=LABELS,zero_division=0,output_dict=True),ensure_ascii=False,indent=2),encoding='utf-8')
            mlflow.log_artifact(str(rep_path),artifact_path='reportes')
            records.append({'modelo':model_name,**values, 'mejores_parametros':json.dumps(gs.best_params_,ensure_ascii=False),'run_id':mlflow.active_run().info.run_id})
            predictions.extend({'modelo':model_name,'id':rid,'texto':tx,'clase_real':true,'prediccion':prediction} for rid,tx,true,prediction in zip(test.id,test_x,test_y,pred))
            print(model_name,'F1 macro:',round(values['f1_macro'],4),'falsas elegibilidades:',values['false_eligibility_count'])
    metrics=pd.DataFrame(records)
    metrics.to_csv(output/'metricas.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(predictions).to_csv(output/'predicciones.csv',index=False,encoding='utf-8-sig')
    metadata={'seed':SEED,'dataset_sha256':sha256(data_path),'mlflow_tracking_uri':tracking_uri,'n_train':len(train),'n_test':len(test),'notas':'AUC OvR sobre puntajes, no probabilidades calibradas para LinearSVC. Holdout sintetico de solo 26 registros.'}
    (output/'metadatos.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Archivos de resultados:',output)
    print('Panel MLflow: mlflow ui --backend-store-uri', tracking_uri, '--port 5000')
    return metrics

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--data',type=Path,default=DEFAULT_DATA)
    parser.add_argument('--output',type=Path,default=RESULTS)
    args=parser.parse_args()
    main(args.data,args.output)
