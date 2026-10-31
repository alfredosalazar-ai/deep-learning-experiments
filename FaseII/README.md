# Fase II - Ejecución de CHATBOT CIMA

Prototipo académico para clasificar consultas operativas sintéticas mediante procesamiento de lenguaje natural (NLP). Integra una interfaz web, una API REST con FastAPI y el pipeline de Regresión Logística entrenado en la Actividad 5. La construcción y las pruebas de contenedor se ejecutan en GitHub Actions; la aplicación está desplegada en Render.

> **Aplicación desplegada:** https://chatbot-cima-fase2.onrender.com/  
> **API Swagger/OpenAPI:** https://chatbot-cima-fase2.onrender.com/docs  
> **Health check:** https://chatbot-cima-fase2.onrender.com/health

## Arquitectura

- **Frontend:** HTML, CSS y JavaScript servidos por FastAPI.
- **Backend:** API REST construida con FastAPI.
- **Modelo:** `modelos/Regresion_Logistica.joblib`, pipeline TF-IDF + Regresión Logística proveniente de la Actividad 5.
- **Contenedor:** `Dockerfile` basado en `python:3.12-slim`.
- **Integración continua:** workflow `.github/workflows/fase2-docker.yml`, ubicado en la raíz del repositorio (fuera de `FaseII/`). Ejecuta pruebas automatizadas, construye la imagen Docker y valida el contenedor mediante solicitudes HTTP.
- **Despliegue:** Render Web Service con runtime Docker.

## Entorno de ejecución y decisión de despliegue

La ejecución de esta fase se realizó deliberadamente en infraestructura de nube. La decisión respondió a las limitaciones de disponibilidad y uso del equipo de cómputo laboral y a que no se contó con acceso a un equipo personal para preparar y ejecutar un entorno Docker local. Por este motivo, **no se realizó una ejecución local del contenedor** y no se presenta el despliegue remoto como si fuera una validación local.

Para mantener la reproducibilidad y validar el contenedor sin depender de una instalación local de Docker, se adoptó el siguiente flujo:

1. **GitHub** aloja el código fuente, el `Dockerfile`, las dependencias, las pruebas y el workflow.
2. **GitHub Actions**, mediante un runner alojado por GitHub, instala las dependencias de prueba, ejecuta `pytest`, construye la imagen Docker y prueba el contenedor mediante solicitudes HTTP.
3. **Render** construye y ejecuta la aplicación desde el repositorio y publica la interfaz y la API.
4. La validación funcional se realiza desde la URL pública y desde Swagger (`/docs`), con consultas sintéticas y comprobaciones de `/health`.

Esta estrategia permitió comprobar la construcción de la imagen, el arranque del servicio, la carga del modelo y la comunicación entre frontend y backend en entornos alojados. **La limitación respecto de la rúbrica es que estas comprobaciones se realizaron en la nube y no acreditan una ejecución local**, requisito que se deja explícitamente identificado. La decisión priorizó un entorno disponible, reproducible y con evidencia verificable, sin afirmar una actividad que no se realizó.

## Endpoints

| Método | Ruta | Propósito |
|---|---|---|
| `GET` | `/` | Interfaz web de clasificación. |
| `GET` | `/health` | Comprueba la disponibilidad de la API y que el modelo esté cargado. |
| `POST` | `/predict` | Clasifica una consulta y devuelve clase, puntaje individual y decisión de enrutamiento. |
| `GET` | `/docs` | Documentación interactiva Swagger/OpenAPI. |

Ejemplo de petición a `POST /predict`:

```json
{
  "texto": "Solicito confirmar el pago asociado al folio 12345."
}
```

La respuesta incluye `clase_predicha`, `decision_operativa`, `requiere_revision_humana`, `puntaje_individual`, `umbral_individual`, `version_modelo` y una advertencia operativa.

## Política de enrutamiento

La aplicación permite la aceptación automatica únicamente cuando se cumplen simultáneamente estas condiciones:

1. La clase predicha es `INDIVIDUAL`.
2. El puntaje individual alcanza o supera el umbral configurado.

El umbral registrado en el despliegue validado es `0.276334` (`INDIVIDUAL_THRESHOLD`). Los demás casos se derivan a `REVISION_HUMANA`. La clasificación es informativa: no confirma transacciones, no autoriza pagos ni sustituye controles deterministas o revisión humana.

## Seguridad y alcance

- Prototipo académico evaluado con consultas y datos sintéticos; no utiliza transacciones bancarias reales.
- No introducir datos personales, credenciales, folios reales ni información confidencial.
- El servicio no incorpora autenticación ni controles empresariales; no debe exponerse como sistema productivo.
- Cargar exclusivamente artefactos `joblib` procedentes de una fuente confiable: la deserialización de archivos manipulados puede ejecutar código.
- El umbral proviene de la evaluación experimental de Actividad 6 y requiere nueva evaluación con un conjunto de datos independiente, más amplio y representativo antes de cualquier uso operativo.
- Los resultados observados en muestras pequeñas no constituyen evidencia suficiente de desempeño en producción.

## Publicación y validación en GitHub

La aplicación reside en `FaseII/` dentro de la rama `main`. El workflow de Docker debe permanecer en `.github/workflows/fase2-docker.yml` en la raíz del repositorio, no dentro de `FaseII/`.

Para validar un cambio:

1. Publicar el commit en `main`.
2. Abrir la pestaña **Actions** del repositorio.
3. Seleccionar **Fase II - prueba y construcción Docker**.
4. Confirmar que finalicen correctamente los pasos de instalación, `pytest`, construcción de imagen y prueba HTTP del contenedor.
5. Si un trabajo falla, revisar el log del paso correspondiente antes de aceptar un despliegue.

Las ejecuciones exitosas observadas durante esta entrega se documentan en `docs/Validacion_y_Pruebas_FaseII_CHATBOT_CIMA.pdf` y en `evidencias/capturas.pdf`.

## Despliegue en Render

### Configuración desplegada y comprobada

El servicio `chatbot-cima-fase2` se creó desde el repositorio `alfredosalazar-ai/deep-learning-experiments`, rama `main`, con runtime **Docker**, región **Oregon (US West)** y plan **Free**. La configuración visible en el formulario al crear el servicio fue:

| Campo de Render | Valor utilizado |
|---|---|
| Name | `chatbot-cima-fase2` |
| Branch | `main` |
| Language | `Docker` |
| Region | `Oregon (US West)` |
| Root Directory | `FaseII` |
| Docker Build Context Directory | `FaseII/.` |
| Dockerfile Path | `FaseII/Dockerfile` |
| Health Check Path | `/health` |
| Instance Type | `Free` (`$0/month`, al momento del despliegue) |
| Registry Credential | `No credential` |
| Docker Command | Vacío; se utiliza el comando definido en el Dockerfile. |
| Auto-Deploy | `On Commit` |

**Nota sobre las rutas:** los valores anteriores reproducen la configuración mostrada en las capturas del asistente de Render y que produjo el despliegue `Live`. La documentación actual de Render indica que Dockerfile Path y Docker Build Context Directory operan relativos al directorio raíz del servicio cuando se define `Root Directory`. Al recrear o editar el servicio, revisar los valores que el Dashboard muestra después de estáblecer `Root Directory`; no duplicar el prefijo `FaseII` si Render ya ajustó las rutas. Referencias: [Render - Monorepo Support](https://render.com/docs/monorepo-support) y [Render - Docker](https://render.com/docs/docker).

### Procedimiento de despliegue

1. Publicar `FaseII/` en la rama `main`.
2. En Render, crear un **Web Service** y conectar `alfredosalazar-ai/deep-learning-experiments`.
3. Seleccionar runtime **Docker**.
4. Definir el directorio raíz de la aplicación como `FaseII` y comprobar las rutas del Dockerfile y del contexto de construcción en el Dashboard.
5. Seleccionar el plan de cómputo requerido. En esta entrega se utilizó **Free**; comprobar el precio mostrado antes de confirmar cualquier cambio de plan.
6. Configurar el Health Check Path como `/health`.
7. Mantener vacíos `Docker Command` y `Pre-Deploy Command`, salvo que una modificación futura del proyecto requiera lo contrario.
8. Iniciar el despliegue y revisar los logs hasta confirmar `Deploy succeeded` / `Live`.
9. Probar `/`, `/health`, `/docs` y una solicitud sintética a `/predict`.

### Comportamiento del plan gratuito

Render Free suspende una instancia web después de un periodo de inactividad (actualmente, 15 minutos sin tráfico entrante) y la reactiva cuando recibe una nueva solicitud. La primera solicitud después de la suspensión puede tardar alrededor de un minuto. Esto no equivale a disponibilidad continua; antes de una demostración o evaluación, abrir la aplicación y esperar a que termine el arranque. Consultar las limitaciones vigentes en [Render - Free](https://render.com/docs/free).

## Pruebas

### Automatizadas (GitHub Actions)

El workflow ejecuta `pytest -q`, construye la imagen Docker y comprueba el servicio dentro del contenedor, incluyendo `/health` y una inferencia HTTP.

### Funcionales de interfaz web

Se documentaron cuatro consultas sintéticas desde la interfaz. Las predicciones observadas fueron:

| Prueba | Clase predicha | Resultado de enrutamiento |
|---|---|---|
| Individual de referencia | `INDIVIDUAL` | `REVISION_HUMANA` (puntaje 0.2651, inferior al umbral). |
| Individual con mayor contexto | `AMBIGUA` | `REVISION_HUMANA`. |
| Solicitud de paquete | `FUERA_ALCANCE` | `REVISION_HUMANA`. |
| Depósito sin folio | `AMBIGUA` | `REVISION_HUMANA`. |

### Funcionales de API (Swagger)

Se ejecutaron ocho pruebas desde `/docs`:

| ID | Escenario | Resultado observado |
|---|---|---|
| API-01 | `GET /health` | HTTP 200; `status=ok`; `model_loaded=true`. |
| API-02 | Consulta individual de referencia | HTTP 200; `INDIVIDUAL`; puntaje `0.2651486888`; revisión humana. |
| API-03 | Consulta de paquete | HTTP 200; `PAQUETE`; puntaje `0.2357329503`; revisión humana. |
| API-04 | Consulta ambigua | HTTP 200; `AMBIGUA`; puntaje `0.2344216569`; revisión humana. |
| API-05 | Consulta turística ajena al alcance | HTTP 200; predicha `AMBIGUA` en lugar de `FUERA_ALCANCE`; revisión humana. Hallazgo de clasificación. |
| API-06 | Texto vacio | HTTP 422; `string_too_short`. |
| API-07 | Campo `texto` ausente | HTTP 422; `missing`. |
| API-08 | Texto de 5,001 caracteres | HTTP 422; `string_too_long`; límite de 5,000 caracteres. |

Las evidencias completas están en `evidencias/capturas.pdf`. Las pruebas muestran el comportamiento de la versión desplegada, no una garantía de generalización. En particular, la consulta turística fue clasificada como `AMBIGUA`, lo que evidencia una limitación en la separación entre `AMBIGUA` y `FUERA_ALCANCE`.

## Estructura del proyecto

```text
FaseII/
|-- backend/
|-- docs/
|-- evidencias/
|-- frontend/
|-- modelos/
|-- tests/
|-- Dockerfile
|-- README.md
|-- requirements.txt
```

El workflow se encuentra fuera de esta carpeta:

```text
.github/workflows/fase2-docker.yml
```

## Documentación y evidencias

- `docs/Manual_Despliegue_Nube_CHATBOT_CIMA.pdf`: procedimiento de despliegue y configuración en la nube.
- `docs/Validacion_y_Pruebas_FaseII_CHATBOT_CIMA.pdf`: resultados, observaciones y limitaciones de validación.
- `evidencias/capturas.pdf`: capturas de la interfaz, las ocho pruebas de API y las evidencias de CI/CD/despliegue.
- `evidencias/enlace_despliegue.txt`: URL de la aplicación y endpoints de comprobación.
- `evidencias/README.md`: índice de los archivos de evidencia.
