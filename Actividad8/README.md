# CHATBOT CIMA - Actividad 8 | Observabilidad y respuesta a incidentes

**Estado:** Iteración 2 validada en GitHub Actions y registro de cinco ejecuciones en MLflow.  
**Entorno:** laboratorio académico 100 % en la nube, con datos sintéticos y escenarios offline.  
**Alcance:** los resultados aqui presentados **no son monitoreo continuo de Render**, ni pruebas de desempeño del modelo productivo.

## 1. Objetivo

Evaluar la observabilidad y la capacidad de respuesta de CHATBOT CIMA mediante indicadores técnicos, SLO, presupuestos de error, alertas con control de ruido, detección de cambios de distribución, simulación de incidentes y ejecución controlada de runbooks. La Actividad 8 aprovecha la arquitectura de Fase II sin modificar el modelo, la API desplegada ni los datos institucionales.

## 2. Resultados ejecutados y verificables

### 2.1. GitHub Actions

| Evidencia | Resultado |
|---|---|
| Workflow exitoso | `actividad8-observabilidad_iteracion2.yml` |
| Ejecucion | `#4 - evitar duplicados` |
| Rama / commit | `main` / `c0d6991` |
| Job | `test-observability` |
| Estado / duracion | **Success** / 23 segundos |
| Artefacto | `cima-a8-simulación` (98.8 KB) |

[Ver ejecuciones de GitHub Actions](https://github.com/alfredosalazar-ai/deep-learning-experiments/actions)

El resultado verde verifica las pruebas y las simulaciones **offline** ejecutadas en GitHub. No implica que se hayan efectuado mediciones en vivo de Render. Se observo una advertencia de compatibilidad con Node.js 20 en acciones de GitHub; no impidio esta ejecución.

### 2.2. Tres incidentes simulados

| Escenario | Antes | Durante el incidente | Despues de recuperar | Runbook |
|---|---:|---:|---:|---|
| INC-01 - Latencia P95 | 450 ms | **7,200 ms**; limite 3,000 ms | 520 ms | RB-02 |
| INC-02 - PSI de clases | 0.000 | **2.869**; limite crítico 0.250 | 0.000 | RB-03 |
| INC-03 - Errores HTTP 5xx | 0 % | **20 %**; limite 1 % | 0 % | RB-01 |

Las acciones y recuperaciones se realizaron sobre estados aislados de laboratorio; **no** se reinicio Render, no se hizo rollback y no se público ningun modelo nuevo.

![INC-01: latencia simulada](results/dashboards/INC-01_indicador.png)

### 2.3. Alertas y control de ruido

- Primera detección: **1 alerta emitida**.
- Repeticion a los 2 minutos: **0 emitidas y 1 suprimida**.
- Nueva detección después de 31 minutos: **1 emitida**.
- Ventana de supresión (*cooldown*): **30 minutos**.
- Tres runbooks registraron recuperación simulada verificada.

**Nota de interpretacion:** en una ejecución con estado temporal reutilizado, cinco alertas figuraron como suprimidas. La prueba secuencial anterior es la que demuestra de manera controlada la emisión inicial, supresión y reemision.

[Consola de alertas](results/incidentes/consola_alertas_demo.txt) | [Registro de runbooks](results/incidentes/runbooks_ejecutados_demo.json) | [Dashboard HTML](results/dashboards/dashboard_simulado.html)

### 2.4. Calidad predictiva: demostración ficticia

Se utilizaron **32 pares de etiquetas y predicciones ficticias** para comprobar el cálculo de indicadores y la activacion de alertas. No son inferencias verificadas contra el modelo de Render.

| Indicador | Referencia simulada | Degradacion simulada | Umbral experimental |
|---|---:|---:|---:|
| Accuracy | 87.50 % | **68.75 %** | 80 % |
| F1 macro | 88.09 % | **69.68 %** | 80 % |

El experimento de calidad registro, ademas, precisión macro de **86.11 %**, recall macro de **68.75 %**, dos alertas de calidad y diez falsas elegibilidades en el escenario ficticio. Estos datos ilustran el mecanismo de monitoreo; **no establecen el desempeño real de CIMA**.

![Calidad ficticia](results/dashboards/calidad_simulada.png)

[Indicadores de calidad en JSON](results/metricas/calidad_demo.json)

## 3. Registro y trazabilidad en MLflow

Desde Google Colab se importo el artefacto de GitHub Actions y se verificaron mediante la API de seguimiento de MLflow **cinco runs finalizados** en el experimento `CIMA_Actividad8_Observabilidad_Simulada`.

| Run | Tipo | Metrica destacada | Estado |
|---|---|---|---|
| `INC-01_incidente_offline` | Incidente | P95 final **520 ms** | `FINISHED` |
| `INC-02_incidente_offline` | Incidente | PSI final **0.000** | `FINISHED` |
| `INC-03_incidente_offline` | Incidente | Disponibilidad final **100 %** | `FINISHED` |
| `CALIDAD_predicciones_ficticias` | Calidad simulada | Accuracy **68.75 %**; F1 macro **69.68 %** | `FINISHED` |
| `ALERTAS_SLO_y_runbooks` | Alertas | **3 runbooks** registrados; cooldown **30 min** | `FINISHED` |

**Lectura correcta:** los indicadores de los tres incidentes son valores **posteriores a la recuperación**; los maximos del incidente estan documentados en la seccion 2.2 y en los artefactos. El run de calidad contiene valores **ficticios**.

La interfaz web de MLflow 3.18.0 no pudo mostrarse mediante el proxy de Colab por la restricción `Invalid Host header - possible DNS rebinding attack detected`. El almacenamiento y los cinco runs se verificaron directamente con `MlflowClient`, sin deshabilitar las protecciones de seguridad del servidor.

**Notebook:** [Abrir archivo en GitHub](notebooks/CIMA_Actividad8_MLflow_Colab.ipynb)  
**Ejecucion directa:** [Open in Colab](https://colab.research.google.com/github/alfredosalazar-ai/deep-learning-experiments/blob/main/Actividad8/notebooks/CIMA_Actividad8_MLflow_Colab.ipynb)

**Archivos de evidencia exportados desde MLflow:**

- [`evidencias/mlflow/mlflow_resumen_runs.csv`](evidencias/mlflow/mlflow_resumen_runs.csv)
- [`evidencias/mlflow/mlflow_detalle_runs.json`](evidencias/mlflow/mlflow_detalle_runs.json)

Los enlaces anteriores requieren publicar esos dos archivos en `Actividad8/evidencias/mlflow/`. El JSON lista rutas de los artefactos registrados, **no contiene una copia de todos sus archivos**. No se ha demostrado el registro de una nueva versión del modelo en MLflow Model Registry.

## 4. Arquitectura y componentes

`CIMA Fase II (Render) -> monitor HTTP opcional bajo demanda -> registros JSON/JSONL -> reglas SLO y alertas -> dashboard estático`.

En paralelo, `GitHub Actions -> pruebas y simulaciones offline -> artefacto -> Google Colab -> MLflow -> evidencias CSV/JSON`.

| Componente | Funcion |
|---|---|
| `config/alerts.yaml` | Configuración de SLO, umbrales y supresión de alertas |
| `src/monitor.py` | Sondeos opcionales GET `/health` y POST `/predict` sintetico |
| `src/alertas.py`, `src/pipeline.py` | Evaluacion de umbrales, presupuesto y alertas |
| `src/drift.py` | PSI de distribución de categorías; no mide exactitud |
| `src/incidentes.py` | Simulacion de tres incidentes y recuperación |
| `src/laboratorio.py` | Alertas en consola, antirruido y acciones simuladas |
| `src/calidad.py` | Métricas cuando se dispone de etiquetas; demostración ficticia |
| `src/visualizar_laboratorio.py` | Gráficos de incidentes y calidad |
| `src/dashboard.py` | Panel HTML estático de un lote |
| `src/mlflow_registro.py` | Registro de experimentos y artefactos en MLflow |
| `notebooks/CIMA_Actividad8_MLflow_Colab.ipynb` | Ejecucion de MLflow en Colab |
| `docs/Runbooks.md`, `docs/plan_evidencias.md` | Procedimientos y plan de trazabilidad |
| `tests/` | Pruebas automatizadas sin llamadas a servicios externos |

Los eventos generados por el monitor disponen de un `trace_id` local para correlación de sondeos; esto **no** constituye trazado distribuido interoperable.

## 5. Reproducción completamente en la nube

En Google Colab, con entorno CPU:

```python
!git clone https://github.com/alfredosalazar-ai/deep-learning-experiments.git
%cd /content/deep-learning-experiments/Actividad8
!pip install -r requirements.txt
!python -m unittest discover -s tests -v
!python -m src.incidentes
!python -m src.pipeline --simulado
!python -m src.laboratorio
!python -m src.calidad
!python -m src.visualizar_laboratorio
```

Para reproducir MLflow, abrir el [notebook publicado](notebooks/CIMA_Actividad8_MLflow_Colab.ipynb) en Colab y cargar el artefacto `cima-a8-simulación.zip` de una ejecución exitosa de GitHub Actions. **No se requiere GPU.** El entorno de Colab es temporal; exportar los resultados antes de finalizar la sesión.

**Opcional, bajo demanda y separado de las simulaciones:** medición HTTP de la API academica de Fase II:

```python
!python -m src.monitor --solo-health
!python -m src.pipeline
```

Para cuatro consultas sinteticas:

```python
!python -m src.monitor --incluye-predict --consultas 4 --health-checks 5
!python -m src.pipeline
```

No utilizar cron para mantener activa la instancia gratuita de Render. Una instancia suspendida por inactividad puede presentar mayor latencia de inicio. No provocar errores deliberados en el servicio público ni introducir información bancaria real.

## 6. SLO y criterios experimentales

| Indicador | Objetivo o regla |
|---|---|
| Disponibilidad | Al menos 99 % en ventana definida |
| Errores HTTP 5xx | Como máximo 1 % |
| Latencia P95 de `/predict` | Como máximo 3,000 ms con instancia activa y al menos 5 muestras |
| Falsas elegibilidades | Cero observadas en lote etiquetado; informar incertidumbre |
| PSI de categorías | Advertencia desde 0.10; crítico desde 0.25; al menos 30 muestras |
| Antirruido | Cooldown de 30 minutos por codigo; mínimo 10 health checks para alertar disponibilidad |

**Limitaciones:** las ventanas cortas no permiten concluir cumplimiento mensual de SLO. El presupuesto de error exige un período de medición y un volumen suficientes. Una variacion en las clases predichas no prueba por si sola data drift del lenguaje ni degradacion de accuracy. Las comparaciones predictivas requieren etiquetas independientes; los ejemplos ficticios de este laboratorio no sustituyen esa evaluación.

## 7. GitHub, entregables y alcance

- **Entrega oficial:** repositorio GitHub, no ZIP.
- **Workflow confirmado en la ejecución verde:** `.github/workflows/actividad8-observabilidad_iteracion2.yml` en la raiz del repositorio.
- **Evidencia CI:** artefacto `cima-a8-simulación` de GitHub Actions, ejecución #4.
- **Evidencia MLflow:** CSV y JSON exportados desde Google Colab, colocados en `Actividad8/evidencias/mlflow/`.
- **Evidencia documental final:** informe técnico y capturas por integrar una vez terminada la revision academica.

Si también existe `.github/workflows/actividad8-observabilidad.yml`, revisar su contenido antes de retirar la versión duplicada; mantener finalmente un solo workflow oficial. No eliminar historiales ni evidencias previas.

No se implemento monitoreo continuo, notificacion externa real, rollback automático, reentrenamiento automático ni publicacion de modelos. Las acciones correctivas de esta actividad operan exclusivamente sobre estados simulados. Estas limitaciones son explicitas para evitar confundir una prueba academica con un sistema listo para produccion.

## 8. Referencias

- [Repositorio de CHATBOT CIMA](https://github.com/alfredosalazar-ai/deep-learning-experiments)
- [API academica de Fase II](https://chatbot-cima-fase2.onrender.com/)
- [Google SRE - Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Documentación de GitHub Actions](https://docs.github.com/en/actions)
- [Documentación de MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/)
- [Documentación de Python](https://docs.python.org/3/)
