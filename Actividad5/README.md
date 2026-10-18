# Actividad 5 — CHATBOT CIMA | Clasificación supervisada y MLflow

Proyecto académico de clasificación de intención de consultas operativas en cuatro clases: `INDIVIDUAL`, `PAQUETE`, `AMBIGUA` y `FUERA_ALCANCE`. Se comparan **TF-IDF + Regresión Logística** y **TF-IDF + LinearSVC** mediante `GridSearchCV` y validación cruzada estratificada de cuatro pliegues. Los experimentos se registran con **MLflow y SQLite**.

## Fuente y naturaleza de los datos

El dataset de origen (`datos/datos_ini/cima_consultas_original.csv`) contiene **160 consultas sintéticas** creadas para CHATBOT CIMA y publicadas previamente en la Actividad 4. No incorpora movimientos bancarios reales ni la base maestra *Nueva CIE 2.1*. La fuente es un conjunto sintético propio publicado en GitHub, no un corpus de terceros: esto debe distinguirse del requisito académico de usar un dataset público.

La preparación en `fuentes/datos_prep.py` normaliza Unicode y espacios, verifica etiquetas, conserva una copia original inalterada, elimina **32 textos duplicados** y genera **128 textos únicos** con semilla `20261015`. La nueva partición estratificada contiene **102 consultas de entrenamiento y 26 de prueba**; no se comparten textos idénticos entre ambas. Se reservó la prueba para evaluación final, sin emplearla en GridSearchCV.

| Clase | Original | Únicos | Entrenamiento | Prueba |
|---|---:|---:|---:|---:|
| INDIVIDUAL | 40 | 40 | 32 | 8 |
| PAQUETE | 40 | 38 | 30 | 8 |
| AMBIGUA | 40 | 10 | 8 | 2 |
| FUERA_ALCANCE | 40 | 40 | 32 | 8 |
| **Total** | **160** | **128** | **102** | **26** |

**Límite metodológico:** la clase `AMBIGUA` tiene solamente 10 formulaciones distintas y dos en la prueba. Las consultas son sintéticas y pueden compartir patrones de construcción; la deduplicación textual no garantiza independencia semántica. Los resultados no prueban generalización a consultas reales.

## Estructura

```text
Actividad5/
├── datos/
│   ├── datos_ini/                    # CSV original
│   └── datos_limp/                   # CSV limpio y particiones
├── fuentes/
│   ├── datos_prep.py                 # Limpieza reproducible
│   ├── train.py                      # Entrenamiento, evaluación y MLflow
│   └── entrena.ipynb                 # Notebook de Google Colab
├── resultados/
│   ├── entrenamiento/               # Métricas, predicciones, CV, modelos y matrices
│   └── *.png                         # Gráficas exploratorias
├── evidencia_mlflow/
│   ├── mlflow.db                     # Base SQLite exportada
│   ├── mlflow_artifacts/             # Artefactos de las ejecuciones
│   └── modelos_nativos/             # Paquetes MLflow con MLmodel
├── informe_tecnico.pdf
├── requirements.txt
├── README.md
└── CHANGELOG.md
```

## Reproducción

Usar Python 3.11 recomendado (se ejecutó originalmente en Google Colab). Desde `Actividad5/`:

```bash
python -m pip install -r requirements.txt
python fuentes/datos_prep.py
python fuentes/train.py
```

**Importante:** la preparación vuelve a generar los datos limpios y la partición con la semilla indicada. `train.py` utiliza `mlflow.set_tracking_uri()` con la base **SQLite `Actividad5/mlflow.db`**, no el antiguo backend de archivos `mlruns`. Crea el experimento `CIMA_Actividad5_NLP_Supervisado`, ajusta ambos modelos y exporta métricas y artefactos. Si se ejecuta sobre el `mlflow.db` incluido, añadirá nuevas ejecuciones; para una reproducción aislada conviene utilizar una copia del proyecto sin la base histórica.

Para consultar experimentos en un entorno local:

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```

El panel local abre en `http://127.0.0.1:5000`. Algunas rutas de artefactos de la base exportada **apuntan a la sesión original de Colab** y pueden no resolverse tras moverla; por eso se incluyen copias independientes de los artefactos y modelos nativos. El registro exportado es evidencia auditable, no una instalación portátil de MLflow ya reconfigurada.

La alternativa en Colab es ejecutar `fuentes/entrena.ipynb`; no requiere GPU. La instalación y ejecución desde cero podrían variar según la versión de dependencias. `requirements.txt` indica rangos compatibles, no un bloqueo exacto de toda la pila.

## Métodos

- **Modelos:** `TfidfVectorizer` + `LogisticRegression` y `TfidfVectorizer` + `LinearSVC`.
- **Selección:** `GridSearchCV(scoring='f1_macro')`, cuatro pliegues estratificados y semilla `20261015`.
- **Ajustes evaluados:** `C ∈ {0.1, 1, 10}`, pesos de clase `None/balanced`, n-gramas `(1,1)/(1,2)` y `min_df=1/2`.
- **Evaluación:** accuracy, precision/recall/F1 macro, ROC-AUC OvR por puntajes de decisión, tiempo de ajuste, latencia por consulta en lote y falsas elegibilidades.
- **Regla de riesgo:** falsa elegibilidad = clase real distinta de `INDIVIDUAL` predicha como `INDIVIDUAL`; no implica autorización de pagos.

## Resultados observados

Valores tomados de `resultados/entrenamiento/metricas.csv`:

| Métrica | Regresión logística | LinearSVC |
|---|---:|---:|
| Accuracy | 1.0000 | 0.9615 |
| Precision macro | 1.0000 | 0.9722 |
| Recall macro | 1.0000 | 0.8750 |
| F1 macro | **1.0000** | 0.9020 |
| F1 macro CV (media) | **0.9186** | 0.8492 |
| F1 macro CV (desv. est.) | 0.0487 | 0.0914 |
| ROC-AUC OvR | 1.0000 | 1.0000 |
| Falsas elegibilidades (26 pruebas) | **0** | 1 |
| Tiempo GridSearchCV + ajuste | 3.77 s | **1.22 s** |

El mejor candidato **para continuar evaluando** es Regresión Logística. No puede declararse listo para producción: los resultados se obtuvieron con únicamente 26 consultas sintéticas de prueba y cambió la partición respecto a la Actividad 4. Las comparaciones directas de desempeño con BART zero-shot no son controladas ni equivalentes. ROC-AUC 1.0 no implica calibración probabilística; en LinearSVC se calcula con puntajes de decisión.

## Evidencia y trazabilidad

- `resultados/entrenamiento/`: `metricas.csv`, `predicciones.csv`, `gridsearch_*.csv`, matrices y reportes por clase, `metadatos.json`, modelos `.joblib`.
- `evidencia_mlflow/mlflow.db`: registros históricos y parámetros de las dos ejecuciones.
- `evidencia_mlflow/modelos_nativos/`: modelos exportados con `MLmodel`, `model.skops` y dependencias.
- `informe_tecnico.pdf`: análisis comparativo, decisiones y deuda técnica.
- `CHANGELOG.md`: proceso y versiones documentadas.

**Seguridad y operación:** este experimento no valida movimientos ni autoriza pagos. Cualquier integración futura requiere validación con casos nuevos, umbrales de abstención, pruebas de fuga semántica, gobierno del dato, reglas deterministas y revisión humana.
